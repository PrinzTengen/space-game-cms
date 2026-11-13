# ruff: noqa: S106, PLC0415
import time
from http import HTTPStatus

import pytest
from allauth.account.internal.flows.login import record_authentication
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import TOTP
from allauth.mfa.totp.internal.auth import format_hotp_value
from allauth.mfa.totp.internal.auth import generate_totp_secret
from allauth.mfa.totp.internal.auth import hotp_value
from allauth.mfa.utils import decrypt
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.authtoken.models import Token

from space_game.users.tests.factories import UserFactory

pytestmark = [pytest.mark.django_db, pytest.mark.real_mfa]


def code(secret):
    return format_hotp_value(hotp_value(secret, int(time.time()) // 30))


def verified_session(client, user, authenticator):
    client.force_login(user)
    request = RequestFactory().get("/")
    request.user = user
    request.session = client.session
    record_authentication(
        request,
        user,
        "mfa",
        id=authenticator.pk,
        type=authenticator.type,
        reauthenticated=True,
    )
    request.session.save()


def test_admin_login_uses_allauth():
    from django.test import Client

    response = Client().get("/admin/login/")
    assert response.status_code == HTTPStatus.FOUND
    assert reverse("account_login") in response.url


def test_staff_must_enroll_before_first_admin_access(
    client,
    django_capture_on_commit_callbacks,
):
    user = UserFactory(
        is_staff=True,
        is_superuser=True,
        password="A-strong-test-password-32",
    )
    response = client.post(
        reverse("account_login"),
        {
            "login": user.username,
            "password": "A-strong-test-password-32",
            "next": "/admin/",
        },
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.resolver_match.view_name == "mfa_activate_totp"
    assert b"otpauth" not in response.content or b"totp" in response.content
    secret = client.session["mfa.totp.secret"]
    assert not Authenticator.objects.filter(user=user, type="totp").exists()
    assert "totp/activate" in client.get("/admin/").url
    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(reverse("mfa_activate_totp"), {"code": code(secret)})
    response.wsgi_request.session.save()
    assert response.status_code == HTTPStatus.FOUND
    authenticator = Authenticator.objects.get(user=user, type="totp")
    assert secret not in str(authenticator.data)
    assert decrypt(authenticator.data["secret"]) == secret
    assert Authenticator.objects.filter(user=user, type="recovery_codes").exists()
    assert client.get("/admin/").status_code == HTTPStatus.OK


def test_existing_totp_login_requires_valid_second_factor(client):
    user = UserFactory(
        is_staff=True,
        is_superuser=True,
        password="A-strong-test-password-32",
    )
    secret = generate_totp_secret()
    TOTP.activate(user, secret)
    response = client.post(
        reverse("account_login"),
        {
            "login": user.username,
            "password": "A-strong-test-password-32",
            "next": "/admin/",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert reverse("mfa_authenticate") in response.url
    assert "_auth_user_id" not in client.session
    bad = str((int(code(secret)) + 1) % 1000000).zfill(6)
    assert (
        client.post(reverse("mfa_authenticate"), {"code": bad}).status_code
        == HTTPStatus.OK
    )
    assert "_auth_user_id" not in client.session
    response = client.post(reverse("mfa_authenticate"), {"code": code(secret)})
    assert response.status_code == HTTPStatus.FOUND
    assert client.get("/admin/").status_code == HTTPStatus.OK


def test_session_without_mfa_proof_cannot_bypass_admin_or_cms(client):
    user = UserFactory(is_staff=True, is_superuser=True)
    TOTP.activate(user, generate_totp_secret())
    client.force_login(user)
    for path in [
        "/admin/",
        "/admin/cms/pagecontent/",
        "/oauth/applications/",
        "/api/users/",
    ]:
        response = client.get(path)
        assert response.status_code == HTTPStatus.FOUND
        assert reverse("mfa_reauthenticate") in response.url


def test_proof_for_another_user_does_not_verify_staff_session(client):
    user = UserFactory(is_staff=True, is_superuser=True)
    other = UserFactory(is_staff=True)
    authenticator = TOTP.activate(other, generate_totp_secret()).instance
    verified_session(client, user, authenticator)
    assert client.get("/admin/").status_code == HTTPStatus.FOUND


def test_staff_cannot_use_password_only_api_tokens(client):
    user = UserFactory(is_staff=True, password="A-strong-test-password-32")
    response = client.post(
        "/api/auth-token/",
        {"username": user.username, "password": "A-strong-test-password-32"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    token = Token.objects.create(user=user)
    response = client.get("/api/users/", HTTP_AUTHORIZATION="Token " + token.key)
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_staff_cannot_remove_required_totp(client):
    user = UserFactory(is_staff=True, is_superuser=True)
    authenticator = TOTP.activate(user, generate_totp_secret()).instance
    verified_session(client, user, authenticator)
    response = client.post(reverse("mfa_deactivate_totp"))
    assert response.status_code == HTTPStatus.OK
    assert Authenticator.objects.filter(pk=authenticator.pk).exists()
