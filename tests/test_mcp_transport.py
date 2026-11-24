import json
import secrets
from datetime import timedelta
from http import HTTPStatus

import httpx2
import pytest
from allauth.mfa.totp.internal.auth import TOTP
from allauth.mfa.totp.internal.auth import generate_totp_secret
from django.conf import settings
from django.utils import timezone
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application

from space_game.control.mcp import create_server
from space_game.users.tests.factories import UserFactory

pytestmark = [pytest.mark.anyio, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def transport_token():
    user = UserFactory(is_staff=True, is_superuser=True)
    TOTP.activate(user, generate_totp_secret())
    application = Application.objects.create(
        name="Transport test",
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
    )
    token = secrets.token_urlsafe(32)
    AccessToken.objects.create(
        user=user,
        application=application,
        token=token,
        scope="mcp:read",
        resource=[settings.MCP_RESOURCE_URL],
        expires=timezone.now() + timedelta(minutes=5),
    )
    return user, token


async def test_streamable_http_sdk_handshake_tools_and_scope_enforcement(
    transport_token,
):
    user, token = transport_token
    server = create_server()
    app = server.streamable_http_app(json_response=True, stateless_http=True)
    async with (
        app.router.lifespan_context(app),
        httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            headers={"Authorization": "Bearer " + token},
        ) as http,
        streamable_http_client(
            settings.MCP_RESOURCE_URL,
            http_client=http,
        ) as (read, write),
        ClientSession(read, write) as session,
    ):
        initialized = await session.initialize()
        assert initialized.server_info.name == "Space Game Management"
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        assert {
            "pages_write",
            "plugins_write",
            "media_upload",
            "content_versions",
            "records_write",
        }.issubset(names)
        result = await session.call_tool("whoami", {})
        assert not result.is_error
        assert json.loads(result.content[0].text)["user_id"] == str(user.pk)
        denied = await session.call_tool(
            "records_write",
            {
                "model": "auth.group",
                "action": "create",
                "values": {"name": "Denied by scope"},
            },
        )
        assert denied.is_error
        assert "Permission denied" in denied.content[0].text


async def test_transport_rejects_missing_tokens_origin_and_serves_discovery(
    settings,
    transport_token,
):
    settings.ALLOWED_HOSTS = ["localhost"]
    from config.asgi import application as app  # noqa: PLC0415

    async with (
        app.router.lifespan_context(app),
        httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app)) as http,
    ):
        response = await http.post(
            settings.MCP_RESOURCE_URL,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'resource_metadata="' in response.headers["www-authenticate"]
        response = await http.get(
            settings.MCP_BASE_URL + "/.well-known/oauth-protected-resource/mcp",
        )
        assert response.status_code == HTTPStatus.OK
        assert "mcp:write" in response.json()["scopes_supported"]
        _, token = transport_token
        response = await http.post(
            settings.MCP_RESOURCE_URL,
            headers={
                "Authorization": "Bearer " + token,
                "Origin": "https://attacker.example",
            },
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
