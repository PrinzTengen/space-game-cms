from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    rate = "10/minute"


class PublicUserAuthToken(ObtainAuthToken):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["user"].is_staff:
            msg = "Administrator password-only tokens are disabled."
            raise PermissionDenied(msg)
        return super().post(request, *args, **kwargs)
