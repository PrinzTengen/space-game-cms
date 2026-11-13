from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.authentication import get_authentication_records
from allauth.account.internal.flows.login import record_authentication
from allauth.mfa.models import Authenticator
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from space_game.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def post_login(self, request, user, **kwargs):
        response = super().post_login(request, user, **kwargs)
        if (
            user.is_staff
            and not Authenticator.objects.filter(user=user, type="totp").exists()
        ):
            methods = get_authentication_records(request, user)
            if methods and methods[-1].get("method") == "password":
                record_authentication(request, user, "password", reauthenticated=True)
        return response

    def get_login_stages(self):
        return [
            "space_game.control.security.StaffEmailVerificationStage"
            if stage == "allauth.account.stages.EmailVerificationStage"
            else stage
            for stage in super().get_login_stages()
        ]

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
