# ruff: noqa: S106
from http import HTTPStatus

import pytest
from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework.authtoken.models import Token

from space_game.users.adapters import AccountAdapter
from space_game.users.tests.factories import UserFactory

pytestmark = [pytest.mark.django_db, pytest.mark.real_mfa]


@pytest.mark.parametrize(
    "path",
    [
        "/accounts/login/",
        "/accounts/signup/",
        "/accounts/discord/login/",
        "/admin/security/signup/",
        "/admin/security/password/reset/",
        "/api/auth-token/",
    ],
)
def test_public_auth_endpoints_are_disabled(client, path, settings):
    settings.ACCOUNT_ALLOW_REGISTRATION = True
    assert client.get(path).status_code == HTTPStatus.NOT_FOUND
    assert (
        client.post(path, {"login": "someone", "password": "irrelevant"}).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_nonstaff_password_cannot_login_at_admin_entry(client):
    user = UserFactory(password="A-strong-test-password-32")
    assert (
        authenticate(username=user.username, password="A-strong-test-password-32")
        is None
    )
    response = client.post(
        reverse("account_login"),
        {"login": user.username, "password": "A-strong-test-password-32"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.context["form"].errors
    assert "_auth_user_id" not in client.session
    assert client.get("/admin/").url.startswith("/admin/login/")


def test_only_active_staff_can_authenticate():
    user = UserFactory(is_staff=True, password="A-strong-test-password-32")
    assert (
        authenticate(username=user.username, password="A-strong-test-password-32")
        == user
    )
    user.is_active = False
    user.save()
    assert (
        authenticate(username=user.username, password="A-strong-test-password-32")
        is None
    )


def test_nonstaff_existing_session_and_api_token_do_not_authenticate(client):
    user = UserFactory()
    client.force_login(user)
    assert client.get("/admin/").url.startswith("/admin/login/")
    token = Token.objects.create(user=user)
    response = client.get("/api/users/", HTTP_AUTHORIZATION="Token " + token.key)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_signup_adapter_is_closed_even_with_setting_override(settings, rf):
    settings.ACCOUNT_ALLOW_REGISTRATION = True
    assert not AccountAdapter().is_open_for_signup(rf.get("/admin/security/signup/"))


def test_staff_login_username_is_case_insensitive(client):
    user = UserFactory(
        username="MissionLead",
        password="A-strong-test-password-32",
        is_staff=True,
    )
    assert (
        authenticate(username="missionlead", password="A-strong-test-password-32")
        == user
    )
    response = client.post(
        reverse("account_login"),
        {"login": "MISSIONLEAD", "password": "A-strong-test-password-32"},
    )
    assert response.status_code == HTTPStatus.FOUND
    assert client.session["_auth_user_id"] == str(user.pk)
