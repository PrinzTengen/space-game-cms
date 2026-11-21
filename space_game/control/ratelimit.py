"""Rate limits for the staff-only surfaces: admin, OAuth and the MCP endpoint.

The admin prefix is read from ``settings.ADMIN_URL`` on every request, so the
limits follow the env-configurable admin location. The MCP endpoint is mounted
as its own ASGI app (see ``config/asgi.py``) and never passes through Django
middleware, so it gets a small ASGI wrapper on top of the same counters.

Clients are keyed by ``REMOTE_ADDR``. Behind Traefik that is only the real
client address when the app server trusts the proxy's ``X-Forwarded-For``
(``--forwarded-allow-ips`` in ``compose/production/django/start``).
"""

from types import SimpleNamespace

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpResponse
from django_ratelimit import ALL
from django_ratelimit.core import get_usage

DEFAULT_RATES = {
    # Every request below ADMIN_URL (pages, changelists, autocomplete, ...).
    "admin": "300/m",
    # POSTs that check secrets: password login, TOTP, recovery codes, reauth.
    "admin-auth": "10/m",
    # OAuth authorize/token/revoke used by MCP clients.
    "oauth": "30/m",
    # Dynamic client registration is unauthenticated, keep it rare.
    "oauth-register": "10/h",
    # All MCP calls per client address.
    "mcp": "120/m",
    # MCP responses with 401 (missing, expired or forged bearer tokens).
    "mcp-auth-failure": "30/h",
}


def rate(group):
    return getattr(settings, "STAFF_RATE_LIMITS", {}).get(group, DEFAULT_RATES[group])


def _hit(request, group, *, increment=True):
    """Return seconds until the window resets when ``group`` is exhausted."""
    usage = get_usage(
        request,
        group=group,
        key="ip",
        rate=rate(group),
        method=ALL,
        increment=increment,
    )
    if not usage:
        return None
    # A peek (no increment) must block once the budget is used up, not after.
    exhausted = usage["should_limit"] or (
        not increment and usage["count"] >= usage["limit"]
    )
    return max(int(usage["time_left"]), 1) if exhausted else None


def too_many_requests(retry_after):
    response = HttpResponse(
        "Too many requests. Please wait and try again.",
        status=429,
        content_type="text/plain; charset=utf-8",
    )
    response["Retry-After"] = str(retry_after)
    return response


class StaffRateLimitMiddleware:
    """Throttle admin and OAuth routes per client IP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for group in self.groups(request):
            retry_after = _hit(request, group)
            if retry_after:
                return too_many_requests(retry_after)
        return self.get_response(request)

    @staticmethod
    def groups(request):
        path = request.path_info
        admin = "/" + settings.ADMIN_URL.lstrip("/")
        if path.startswith(admin):
            groups = ["admin"]
            sub = path[len(admin) :]
            if request.method == "POST" and sub.startswith(("login/", "security/")):
                groups.append("admin-auth")
            return groups
        if path.startswith("/oauth/"):
            groups = ["oauth"]
            if path.startswith("/oauth/register"):
                groups.append("oauth-register")
            return groups
        return []


def _scope_request(scope):
    """Minimal request object for django-ratelimit's ``ip`` key."""
    client = scope.get("client") or ("", 0)
    return SimpleNamespace(
        method=scope.get("method", "GET"),
        META={"REMOTE_ADDR": client[0] or "unknown"},
    )


class MCPRateLimitMiddleware:
    """ASGI wrapper that throttles all MCP traffic and repeated 401s per IP."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = _scope_request(scope)
        retry_after = await sync_to_async(_hit)(
            request,
            "mcp-auth-failure",
            increment=False,
        ) or await sync_to_async(_hit)(request, "mcp")
        if retry_after:
            await self._reject(send, retry_after)
            return

        async def watch_status(message):
            if message["type"] == "http.response.start" and message["status"] == 401:  # noqa: PLR2004
                await sync_to_async(_hit)(request, "mcp-auth-failure")
            await send(message)

        await self.app(scope, receive, watch_status)

    @staticmethod
    async def _reject(send, retry_after):
        body = b'{"error":"rate_limited","error_description":"Too many requests"}'
        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"retry-after", str(retry_after).encode()),
                ],
            },
        )
        await send({"type": "http.response.body", "body": body})
