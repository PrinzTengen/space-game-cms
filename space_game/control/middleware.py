from allauth.mfa.models import Authenticator
from django.conf import settings
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import urlencode

from space_game.control.security import staff_mfa_verified


class StaffMFAMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        name = request.resolver_match.view_name if request.resolver_match else ""
        if name.startswith("account_") and name not in {
            "account_login",
            "account_logout",
            "account_reauthenticate",
            "account_inactive",
            "account_change_password",
            "account_email",
        }:
            raise Http404
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return None
        if request.path.startswith(
            (settings.STATIC_URL, settings.MEDIA_URL, "/.well-known/"),
        ):
            return None
        if name in {
            "account_login",
            "account_logout",
            "admin:logout",
            "account_reauthenticate",
        }:
            return None
        if staff_mfa_verified(request):
            return None
        enrolled = Authenticator.objects.filter(
            user=user,
            type=Authenticator.Type.TOTP,
        ).exists()
        target = "mfa_reauthenticate" if enrolled else "mfa_activate_totp"
        if name == target:
            return None
        request.session.setdefault("staff_mfa_next", request.get_full_path())
        return HttpResponseRedirect(
            reverse(target) + "?" + urlencode({"next": request.get_full_path()}),
        )
