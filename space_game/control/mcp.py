# ruff: noqa: C901, PLR0913, PLR0917
"""The management MCP server: OAuth-authenticated, stateless Streamable HTTP."""

from typing import Literal

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import transaction
from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from space_game.control import cms_services
from space_game.control import media_services
from space_game.control import services
from space_game.control.oauth import DjangoTokenVerifier


async def execute(function, *args, write=False, publish=False, **kwargs):
    token = get_access_token()

    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def invoke():
        user = services.actor(
            token,
            "mcp:write" if write else "mcp:read",
        )
        if publish:
            services.actor(token, "mcp:publish")
        return services.plain(function(user, *args, **kwargs))

    try:
        return await invoke()
    except PermissionDenied as exc:
        raise ToolError("Permission denied: " + str(exc)) from None
    except (ValidationError, ObjectDoesNotExist, ValueError, KeyError) as exc:
        raise ToolError(str(exc)) from None
    except OSError:
        msg = "The storage operation failed. Check the upload and try again."
        raise ToolError(msg) from None


def create_server():
    server = MCPServer(
        "Space Game Management",
        version="1.0.0",
        instructions=(
            "Manage this Django CMS using the authenticated administrator's "
            "permissions. Edits stay in drafts; publish explicitly. Use "
            "management_catalog and plugin types/schema before editing. Upload "
            "files in base64 chunks, then attach their returned model/pk "
            "reference to a plugin."
        ),
        token_verifier=DjangoTokenVerifier(),
        auth=AuthSettings(
            issuer_url=settings.MCP_BASE_URL,
            resource_server_url=settings.MCP_RESOURCE_URL,
            required_scopes=["mcp:read"],
            validate_token_resource=True,
        ),
    )
    read = ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        openWorldHint=False,
    )
    write = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        openWorldHint=False,
    )

    @server.tool(annotations=read)
    async def whoami() -> dict:
        """Return the current Django admin identity and granted OAuth scopes."""
        token = get_access_token()
        if token is None:
            msg = "Authentication required."
            raise ToolError(msg)
        return await execute(
            lambda user: {
                "user_id": str(user.pk),
                "username": user.username,
                "scopes": token.scopes,
            },
        )

    @server.tool(annotations=read)
    async def management_catalog() -> list:
        """List manageable Django admin models and their current CRUD permissions."""
        return await execute(services.catalog)

    @server.tool(annotations=read)
    async def records_read(
        model: str,
        action: Literal["list", "get", "schema"] = "list",
        object_id: int | None = None,
        search: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> dict | list:
        """Read registered admin records or their form schema. Sensitive auth models
        are excluded.
        """
        return await execute(
            services.records,
            action,
            model,
            object_id=object_id,
            search=search,
            limit=limit,
            offset=offset,
        )

    @server.tool(annotations=write)
    async def records_write(
        model: str,
        action: Literal["create", "update", "delete"],
        object_id: int | None = None,
        values: dict | None = None,
    ) -> dict:
        """Create, partially edit or delete an admin record using its native admin form
        and permissions.
        """
        return await execute(
            services.records,
            action,
            model,
            object_id=object_id,
            values=values,
            write=True,
        )

    @server.tool(annotations=read)
    async def pages_read(
        action: Literal["list", "get"] = "list",
        content_id: int | None = None,
        language: str = "en",
    ) -> dict | list:
        """Read CMS page-content IDs, page IDs, templates and version states."""
        return await execute(
            cms_services.pages,
            action,
            content_id=content_id,
            language=language,
        )

    @server.tool(annotations=write)
    async def pages_write(
        action: Literal["create", "update", "translate", "delete"],
        content_id: int | None = None,
        values: dict | None = None,
        language: str = "en",
        parent_id: int | None = None,
    ) -> dict:
        """Create/edit/translate CMS pages as drafts. Delete removes the entire page
        and its descendants.
        """
        return await execute(
            cms_services.pages,
            action,
            content_id=content_id,
            values=values,
            language=language,
            parent_id=parent_id,
            write=True,
            publish=action == "delete",
        )

    @server.tool(annotations=read)
    async def plugins_read(
        action: Literal["types", "list"] = "types",
        content_id: int | None = None,
    ) -> list:
        """Discover available plugin form schemas or list a page's placeholders and
        plugin IDs/configuration.
        """
        return await execute(cms_services.plugins, action, content_id=content_id)

    @server.tool(annotations=write)
    async def plugins_write(
        action: Literal["add", "update", "delete", "move"],
        content_id: int,
        slot: str,
        plugin_type: str | None = None,
        plugin_id: int | None = None,
        parent_id: int | None = None,
        values: dict | None = None,
        position: int | None = None,
    ) -> dict:
        """Manage plugins on an explicit page draft. Use the draft's plugin IDs; values
        match the native form schema.
        """
        return await execute(
            cms_services.plugins,
            action,
            content_id=content_id,
            slot=slot,
            plugin_type=plugin_type,
            plugin_id=plugin_id,
            parent_id=parent_id,
            values=values,
            position=position,
            write=True,
        )

    @server.tool(annotations=write)
    async def content_versions(
        action: Literal["list", "draft", "publish", "unpublish", "archive", "discard"],
        kind: Literal["page", "story"],
        content_id: int,
    ) -> dict | list:
        """Manage versioned content. Publish/unpublish requires the separate
        mcp:publish scope and native version permissions.
        """
        return await execute(
            cms_services.versions,
            action,
            kind,
            content_id,
            write=action != "list",
            publish=action in {"publish", "unpublish"},
        )

    @server.tool(annotations=read)
    async def stories_read(
        action: Literal["list", "get"] = "list",
        content_id: int | None = None,
        language: str = "en",
    ) -> dict | list:
        """Read News/Devlog article content and version states."""
        return await execute(
            cms_services.stories,
            action,
            content_id=content_id,
            language=language,
        )

    @server.tool(annotations=write)
    async def stories_write(
        action: Literal["create", "update", "translate", "delete", "metadata"],
        content_id: int | None = None,
        values: dict | None = None,
        language: str = "en",
    ) -> dict:
        """Manage draft articles. Creation needs app_config_id, title and slug. Delete
        removes all translations. Metadata (image_id, category_ids, tags,
        author_id, app_config_id, publication dates) is shared across versions
        and takes effect immediately; it also requires mcp:publish.
        """
        return await execute(
            cms_services.stories,
            action,
            content_id=content_id,
            values=values,
            language=language,
            write=True,
            publish=action in {"delete", "metadata"},
        )

    @server.tool(annotations=read)
    async def media_read(
        action: Literal["list", "get"] = "list",
        file_id: int | None = None,
        folder_id: int | None = None,
        limit: int = 50,
    ) -> dict | list:
        """Read permitted django-filer files and images."""
        return await execute(
            media_services.media,
            action,
            file_id=file_id,
            folder_id=folder_id,
            limit=limit,
        )

    @server.tool(annotations=write)
    async def media_write(
        action: Literal["update", "delete"],
        file_id: int,
        values: dict | None = None,
    ) -> dict:
        """Edit file metadata or delete a file from django-filer. Deleting can break
        existing page references.
        """
        return await execute(
            media_services.media,
            action,
            file_id=file_id,
            values=values,
            write=True,
        )

    @server.tool(annotations=write)
    async def media_upload(
        action: Literal["begin", "chunk", "finish", "abort", "list", "status"],
        upload_id: str | None = None,
        filename: str | None = None,
        size: int | None = None,
        kind: Literal["file", "image"] = "file",
        chunk: str | None = None,
        offset: int | None = None,
        sha256: str = "",
        folder_id: int | None = None,
    ) -> dict:
        """Upload images/files: begin declares size; send base64 chunks of at most 1
        MiB with exact offset; finish validates and creates a public Filer asset.
        The returned reference attaches to frontend plugin fields such as image or
        launcher_file.
        """
        return await execute(
            media_services.uploads,
            action,
            upload_id=upload_id,
            filename=filename,
            size=size,
            kind=kind,
            chunk=chunk,
            offset=offset,
            sha256=sha256,
            folder_id=folder_id,
            write=action not in {"list", "status"},
        )

    return server
