from http import HTTPStatus

import pytest
from asgiref.sync import async_to_sync

from space_game.control.ratelimit import MCPRateLimitMiddleware

pytestmark = pytest.mark.django_db


def test_admin_login_posts_are_throttled_per_ip(client, settings):
    settings.STAFF_RATE_LIMITS = {"admin-auth": "3/m"}
    for _ in range(3):
        response = client.post("/admin/login/", {"login": "x", "password": "y"})
        assert response.status_code != HTTPStatus.TOO_MANY_REQUESTS
    response = client.post("/admin/login/", {"login": "x", "password": "y"})
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert int(response["Retry-After"]) >= 1
    other = client.post(
        "/admin/login/",
        {"login": "x", "password": "y"},
        REMOTE_ADDR="10.0.0.9",
    )
    assert other.status_code != HTTPStatus.TOO_MANY_REQUESTS


def test_admin_limit_follows_configured_admin_url(client, settings):
    settings.ADMIN_URL = "hidden-control/"
    settings.STAFF_RATE_LIMITS = {"admin": "2/m"}
    for _ in range(2):
        client.get("/hidden-control/whatever/")
    assert (
        client.get("/hidden-control/whatever/").status_code
        == HTTPStatus.TOO_MANY_REQUESTS
    )
    # The old default prefix is no longer the admin and is not admin-throttled.
    assert client.get("/admin/").status_code != HTTPStatus.TOO_MANY_REQUESTS


def test_public_pages_are_not_throttled(client, settings):
    settings.STAFF_RATE_LIMITS = {"admin": "1/m"}
    for _ in range(3):
        assert client.get("/i18n/setlang/").status_code != HTTPStatus.TOO_MANY_REQUESTS


def test_oauth_client_registration_is_throttled(client, settings):
    settings.STAFF_RATE_LIMITS = {"oauth-register": "2/h"}
    for _ in range(2):
        client.post("/oauth/register/", {}, content_type="application/json")
    response = client.post("/oauth/register/", {}, content_type="application/json")
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_ratelimit_can_be_disabled(client, settings):
    settings.RATELIMIT_ENABLE = False
    settings.STAFF_RATE_LIMITS = {"admin-auth": "1/m"}
    for _ in range(3):
        response = client.post("/admin/login/", {"login": "x", "password": "y"})
        assert response.status_code != HTTPStatus.TOO_MANY_REQUESTS


def _app(status):
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": status, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    return app


def _call(app, ip="203.0.113.7"):
    sent = []

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "method": "POST", "path": "/mcp", "client": (ip, 1)}
    async_to_sync(app)(scope, receive, send)
    return sent[0]


def test_mcp_requests_are_throttled_per_ip(settings):
    settings.STAFF_RATE_LIMITS = {"mcp": "2/m"}
    app = MCPRateLimitMiddleware(_app(200))
    assert _call(app)["status"] == HTTPStatus.OK
    assert _call(app)["status"] == HTTPStatus.OK
    blocked = _call(app)
    assert blocked["status"] == HTTPStatus.TOO_MANY_REQUESTS
    assert any(name == b"retry-after" for name, _ in blocked["headers"])
    assert _call(app, ip="198.51.100.1")["status"] == HTTPStatus.OK


def test_mcp_blocks_repeated_auth_failures(settings):
    settings.STAFF_RATE_LIMITS = {"mcp-auth-failure": "2/h"}
    app = MCPRateLimitMiddleware(_app(401))
    assert _call(app)["status"] == HTTPStatus.UNAUTHORIZED
    assert _call(app)["status"] == HTTPStatus.UNAUTHORIZED
    assert _call(app)["status"] == HTTPStatus.TOO_MANY_REQUESTS
