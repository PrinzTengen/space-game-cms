import base64
import hashlib
import secrets
from datetime import timedelta
from http import HTTPStatus
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlsplit

import pytest
from allauth.mfa.models import Authenticator
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application

from space_game.control.oauth import DjangoTokenVerifier
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def oauth_staff(client):
    cache.clear()
    user = UserFactory(is_staff=True, is_superuser=True)
    client.force_login(user)
    return user


def app_for(user):
    return Application.objects.create(
        user=user,
        name="Claude test client",
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris="http://127.0.0.1:8976/callback",
    )


def authorization(client, application, verifier):
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    return {
        "client_id": application.client_id,
        "response_type": "code",
        "redirect_uri": application.redirect_uris,
        "scope": "mcp:read mcp:write mcp:publish",
        "state": "expected-state",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "resource": settings.MCP_RESOURCE_URL,
    }


def issued_token(client, user):
    application = app_for(user)
    verifier = secrets.token_urlsafe(64)
    params = authorization(client, application, verifier)
    url = reverse("oauth2_provider:authorize")
    response = client.get(url + "?" + urlencode(params))
    assert response.status_code == HTTPStatus.OK
    data = {
        key: value if value is not None else ""
        for key, value in response.context["form"].initial.items()
    }
    response = client.post(url, {**data, "allow": "on"})
    assert response.status_code == HTTPStatus.FOUND, response.content
    query = parse_qs(urlsplit(response.url).query)
    assert query["state"] == ["expected-state"]
    response = client.post(
        reverse("oauth2_provider:token"),
        {
            "grant_type": "authorization_code",
            "client_id": application.client_id,
            "code": query["code"][0],
            "code_verifier": verifier,
            "redirect_uri": application.redirect_uris,
            "resource": settings.MCP_RESOURCE_URL,
        },
    )
    assert response.status_code == HTTPStatus.OK, response.content
    return response.json()


def test_oauth_discovery_advertises_pkce_resource_and_scopes(client):
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["code_challenge_methods_supported"] == ["S256"]
    assert data["authorization_endpoint"].endswith("/oauth/authorize/")
    assert data["registration_endpoint"].endswith("/oauth/register/")
    assert "password" not in data["grant_types_supported"]
    response = client.get("/.well-known/oauth-protected-resource/mcp")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["resource"] == settings.MCP_RESOURCE_URL
    assert set(response.json()["scopes_supported"]) == {
        "mcp:read",
        "mcp:write",
        "mcp:publish",
    }


def test_pkce_flow_issues_resource_bound_token_after_mfa(oauth_staff, client):
    data = issued_token(client, oauth_staff)
    raw = data["access_token"]
    access = AccessToken.objects.get(user=oauth_staff)
    assert access.resource == [settings.MCP_RESOURCE_URL]
    assert access.token != raw
    verified = async_to_sync(DjangoTokenVerifier().verify_token)(raw)
    assert verified.subject == str(oauth_staff.pk)
    assert "mcp:write" in verified.scopes


def test_tokens_reject_wrong_audience_missing_scope_expiry_and_disabled_staff(
    oauth_staff,
    client,
):

    data = issued_token(client, oauth_staff)
    verify = async_to_sync(DjangoTokenVerifier().verify_token)
    access = AccessToken.objects.get(user=oauth_staff)
    for change in [
        {"resource": []},
        {"resource": ["https://other.example/mcp"]},
        {"scope": "mcp:write"},
        {"expires": timezone.now() - timedelta(seconds=1)},
    ]:
        original = {key: getattr(access, key) for key in change}
        for key, value in change.items():
            setattr(access, key, value)
        access.save()
        assert verify(data["access_token"]) is None
        for key, value in original.items():
            setattr(access, key, value)
        access.save()
    oauth_staff.is_active = False
    oauth_staff.save()
    assert verify(data["access_token"]) is None


def test_resetting_totp_revokes_management_tokens(oauth_staff, client):
    data = issued_token(client, oauth_staff)
    Authenticator.objects.filter(user=oauth_staff, type="totp").delete()
    assert not AccessToken.objects.filter(user=oauth_staff).exists()
    assert (
        async_to_sync(DjangoTokenVerifier().verify_token)(data["access_token"]) is None
    )


def test_nonstaff_cannot_authorize_management_client(client):
    user = UserFactory()
    client.force_login(user)
    app = app_for(user)
    response = client.get(
        reverse("oauth2_provider:authorize")
        + "?"
        + urlencode(authorization(client, app, secrets.token_urlsafe(64))),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_client_registration_cannot_obtain_tokens_without_admin_consent(client):
    cache.clear()
    response = client.post(
        reverse("oauth2_provider:dcr-register"),
        data={
            "client_name": "Claude Code",
            "redirect_uris": ["http://127.0.0.1:8976/callback"],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        },
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.CREATED, response.content
    assert not AccessToken.objects.filter(user__isnull=False).exists()
    assert (
        async_to_sync(DjangoTokenVerifier().verify_token)(
            response.json()["registration_access_token"],
        )
        is None
    )


@pytest.mark.parametrize(
    "redirect",
    [
        "http://evil.example/callback",
        "javascript:alert(1)",
        "https://example.com/callback#fragment",
        123,
    ],
)
def test_registration_rejects_unsafe_callback(client, redirect):
    cache.clear()
    response = client.post(
        reverse("oauth2_provider:dcr-register"),
        data={
            "client_name": "Unsafe",
            "redirect_uris": [redirect],
            "token_endpoint_auth_method": "none",
        },
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert not Application.objects.exists()


def test_authorization_requires_pkce(oauth_staff, client):
    application = app_for(oauth_staff)
    params = authorization(client, application, secrets.token_urlsafe(64))
    params.pop("code_challenge")
    params.pop("code_challenge_method")
    response = client.get(
        reverse("oauth2_provider:authorize") + "?" + urlencode(params),
    )
    assert response.status_code == HTTPStatus.FOUND
    assert parse_qs(urlsplit(response.url).query)["error"] == ["invalid_request"]
    assert not AccessToken.objects.filter(user=oauth_staff).exists()
