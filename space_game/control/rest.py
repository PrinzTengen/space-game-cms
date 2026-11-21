from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from space_game.control.security import staff_mfa_verified


class StaffSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result and result[0].is_staff and not staff_mfa_verified(request._request):  # noqa: SLF001
            msg = "Administrator MFA verification required."
            raise AuthenticationFailed(msg)
        return result
