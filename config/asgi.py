"""
ASGI config for Space Game project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# space_game directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "space_game"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
from contextlib import asynccontextmanager  # noqa: E402
from urllib.parse import urlsplit  # noqa: E402

from django.conf import settings  # noqa: E402
from mcp.server.transport_security import TransportSecuritySettings  # noqa: E402
from starlette.applications import Starlette  # noqa: E402
from starlette.routing import Mount  # noqa: E402

from config.websocket import websocket_application  # noqa: E402
from space_game.control.mcp import create_server  # noqa: E402
from space_game.control.ratelimit import MCPRateLimitMiddleware  # noqa: E402

management_server = create_server()
origin = urlsplit(settings.MCP_BASE_URL)
mcp_starlette = management_server.streamable_http_app(
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[origin.netloc],
        allowed_origins=[settings.MCP_BASE_URL],
    ),
)
mcp_application = MCPRateLimitMiddleware(mcp_starlette)


async def dispatch(scope, receive, send):
    if scope["type"] == "http":
        if scope["path"] in {
            "/mcp",
            "/mcp/",
        }:
            await mcp_application(scope, receive, send)
        else:
            await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)


@asynccontextmanager
async def lifespan(app):
    async with mcp_starlette.router.lifespan_context(mcp_starlette):
        yield


application = Starlette(routes=[Mount("/", app=dispatch)], lifespan=lifespan)
