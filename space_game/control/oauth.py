import hashlib
import ipaddress
import json
from urllib.parse import urlsplit

from allauth.mfa.models import Authenticator
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from mcp.server.auth.provider import AccessToken as MCPAccessToken
from oauth2_provider.http import OAuth2ResponseRedirect
from oauth2_provider.models import AccessToken
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.views import AuthorizationView

from space_game.control.security import staff_mfa_verified

REGISTRATIONS_PER_HOUR = 20


def valid_callback(uri):
    if not isinstance(uri, str):
        return False
    try:
        parsed = urlsplit(uri)
        _ = parsed.port  # Validate malformed ports as well.
    except ValueError:
        return False
    if parsed.username or parsed.password or parsed.fragment:
        return False
    if parsed.scheme == "https" and parsed.hostname:
        return True
    try:
        loopback = ipaddress.ip_address(parsed.hostname or "").is_loopback
    except ValueError:
        loopback = parsed.hostname == "localhost"
    return parsed.scheme == "http" and loopback


class ManagementOAuthValidator(OAuth2Validator):
    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return valid_callback(redirect_uri) and super().validate_redirect_uri(
            client_id,
            redirect_uri,
            request,
            *args,
            **kwargs,
        )


class StaffAuthorizationView(AuthorizationView):
    def redirect(self, redirect_to, application):
        parsed = urlsplit(redirect_to)
        host = parsed.hostname or ""
        try:
            loopback = ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = host == "localhost"
        if parsed.scheme == "http" and loopback:
            return OAuth2ResponseRedirect(redirect_to, ["http", "https"])
        return super().redirect(redirect_to, application)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not staff_mfa_verified(request):
            raise PermissionDenied
        params = request.GET if request.method == "GET" else request.POST
        resources = params.getlist("resource")
        if len(resources) == 1 and resources[0].startswith("["):
            try:
                resources = json.loads(resources[0])
            except ValueError, TypeError:
                resources = []
        if resources != [settings.MCP_RESOURCE_URL]:
            return JsonResponse({"error": "invalid_target"}, status=400)
        return super().dispatch(request, *args, **kwargs)


class LimitedRegistration:
    def has_permission(self, request):
        # Registration creates a client only; staff login, MFA and consent are
        # still required before that client can obtain management access.
        try:
            metadata = json.loads(request.body)
        except ValueError, TypeError:
            return False
        if not isinstance(metadata, dict) or not isinstance(
            metadata.get("redirect_uris"),
            list,
        ):
            return False
        if not all(valid_callback(uri) for uri in metadata["redirect_uris"]):
            return False
        address = request.META.get("REMOTE_ADDR", "unknown")
        key = "mcp-registration:" + hashlib.sha256(address.encode()).hexdigest()
        cache.add(key, 0, 3600)
        try:
            return cache.incr(key) <= REGISTRATIONS_PER_HOUR
        except ValueError:
            return False


class DjangoTokenVerifier:
    @sync_to_async(thread_sensitive=True)
    def verify_token(self, token):
        checksum = hashlib.sha256(token.encode()).hexdigest()
        access = (
            AccessToken.objects.select_related("user", "application")
            .filter(token_checksum=checksum)
            .first()
        )
        if access is None or not access.is_valid(["mcp:read"]):
            return None
        user = access.user
        if user is None or not user.is_active or not user.is_staff:
            return None
        if access.resource != [settings.MCP_RESOURCE_URL]:
            return None
        if not Authenticator.objects.filter(
            user=user,
            type=Authenticator.Type.TOTP,
        ).exists():
            return None
        if (
            access.application is None
            or access.application.authorization_grant_type != "authorization-code"
        ):
            return None
        return MCPAccessToken(
            token=token,
            client_id=access.application.client_id,
            subject=str(user.pk),
            scopes=access.scope.split(),
            expires_at=int(access.expires.timestamp()),
            resource=settings.MCP_RESOURCE_URL,
        )
