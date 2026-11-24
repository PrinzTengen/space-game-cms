import base64
import hashlib
from io import BytesIO

import pytest
from cms.models import PageContent
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.management import call_command
from djangocms_stories.cms_appconfig import StoriesConfig
from filer.models import File
from PIL import Image

from space_game.control import cms_services as cms
from space_game.control import media_services as media
from space_game.control import services
from space_game.control.models import AuditEvent
from space_game.control.models import Upload
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def home():
    return PageContent.objects.get(page__is_home=True, language="en")


def test_manage_page_drafts_and_publish(manager):
    created = cms.pages(
        manager,
        "create",
        values={"title": "MCP page", "slug": "mcp-page"},
    )
    assert created["state"] == "draft"
    updated = cms.pages(
        manager,
        "update",
        content_id=created["id"],
        values={"title": "New title"},
    )
    assert updated["state"] == "draft"
    cms.versions(manager, "publish", "page", updated["id"])
    assert PageContent.objects.get(pk=updated["id"]).title == "New title"
    copied = cms.versions(manager, "draft", "page", updated["id"])
    assert copied["id"] != updated["id"]
    cms.pages(manager, "delete", content_id=copied["id"])
    assert not PageContent.admin_manager.filter(page_id=created["page_id"]).exists()


def test_manage_frontend_plugins_preserves_public_content(manager, client):
    kinds = cms.plugins(manager, "types")
    assert any(item["type"] == "SpaceGameFAQItemPlugin" for item in kinds)
    draft = cms.versions(manager, "draft", "page", home().pk)
    group = cms.plugins(
        manager,
        "add",
        draft["id"],
        "content",
        plugin_type="SpaceGameFAQPlugin",
        values={"title": "Remote FAQ"},
    )
    question = cms.plugins(
        manager,
        "add",
        draft["id"],
        "content",
        plugin_type="SpaceGameFAQItemPlugin",
        parent_id=group["id"],
        values={"question": "Remote question?", "answer": "Original answer"},
    )
    changed = cms.plugins(
        manager,
        "update",
        draft["id"],
        "content",
        plugin_id=question["id"],
        values={"answer": "Changed answer"},
    )
    assert changed["values"]["answer"] == "Changed answer"
    assert b"Remote question?" not in client.get("/").content
    cms.versions(manager, "publish", "page", draft["id"])
    assert b"Changed answer" in client.get("/").content


def test_plugin_constraints_and_published_ids_are_enforced(manager):
    with pytest.raises(ValidationError):
        cms.plugins(
            manager,
            "add",
            home().pk,
            "content",
            plugin_type="SpaceGameFAQPlugin",
            values={"title": "Forbidden"},
        )
    draft = cms.versions(manager, "draft", "page", home().pk)
    with pytest.raises(ValidationError):
        cms.plugins(
            manager,
            "add",
            draft["id"],
            "content",
            plugin_type="SpaceGameFAQItemPlugin",
            values={"question": "No parent", "answer": "No"},
        )
    with pytest.raises(ValidationError):
        cms.plugins(
            manager,
            "add",
            draft["id"],
            "hero",
            plugin_type="SpaceGameHeroPlugin",
            values={"title": "Duplicate"},
        )


def test_links_and_file_reference_forms_work_with_partial_plugin_edits(manager):
    draft = cms.versions(manager, "draft", "page", home().pk)
    cta = cms.plugins(
        manager,
        "add",
        draft["id"],
        "content",
        plugin_type="SpaceGameCTAPlugin",
        values={"title": "Remote CTA"},
    )
    # CTA buttons are native Link / Button children, not CTA fields.
    button = cms.plugins(
        manager,
        "add",
        draft["id"],
        "content",
        plugin_type="TextLinkPlugin",
        parent_id=cta["id"],
        values={
            "name": "Read",
            "link": {"external_link": "https://example.com/read"},
        },
    )
    changed = cms.plugins(
        manager,
        "update",
        draft["id"],
        "content",
        plugin_id=button["id"],
        values={"name": "Read more"},
    )
    assert changed["values"]["name"] == "Read more"
    assert changed["values"]["link"] == {
        "external_link": "https://example.com/read",
    }


def test_native_stories_plugin_form_and_relations(manager):
    draft = cms.versions(manager, "draft", "page", home().pk)
    config = StoriesConfig.objects.get(namespace="stories")
    result = cms.plugins(
        manager,
        "add",
        draft["id"],
        "content",
        plugin_type="BlogLatestEntriesPlugin",
        values={"app_config": config.pk, "latest_posts": 2},
    )
    assert result["type"] == "BlogLatestEntriesPlugin"
    assert result["values"]["app_config"] == config.pk
    assert any(
        item["type"] == "BlogLatestEntriesPlugin" and "app_config" in item["fields"]
        for item in cms.plugins(manager, "types")
    )


def test_story_create_edit_translate_and_publish(manager):
    config = StoriesConfig.objects.get(namespace="stories")
    created = cms.stories(
        manager,
        "create",
        values={
            "app_config_id": config.pk,
            "title": "Remote news",
            "slug": "remote-news",
            "post_text": "<p>First text</p>",
        },
    )
    cms.stories(
        manager,
        "update",
        content_id=created["id"],
        values={"post_text": "<p>Changed</p><script>alert(1)</script>"},
    )
    cms.versions(manager, "publish", "story", created["id"])
    translated = cms.stories(
        manager,
        "translate",
        content_id=created["id"],
        language="de",
        values={
            "title": "Nachricht",
            "slug": "nachricht",
            "post_text": "<p>Deutsch</p>",
        },
    )
    assert translated["state"] == "draft"
    metadata = cms.stories(
        manager,
        "metadata",
        content_id=created["id"],
        values={"tags": ["MCP", "News"]},
    )
    assert set(metadata["metadata"]["tags"]) == {"MCP", "News"}
    assert (
        "<script>"
        not in cms.stories(manager, "get", content_id=created["id"])["post_text"]
    )


def test_admin_record_crud_and_secret_models(manager):
    added = services.records(
        manager,
        "create",
        "auth.group",
        values={"name": "Editors via MCP"},
    )
    assert Group.objects.filter(pk=added["id"]).exists()
    services.records(
        manager,
        "update",
        "auth.group",
        object_id=added["id"],
        values={"name": "Renamed"},
    )
    services.records(manager, "delete", "auth.group", object_id=added["id"])
    assert not Group.objects.filter(pk=added["id"]).exists()
    assert AuditEvent.objects.filter(actor=manager).count() == 3  # noqa: PLR2004
    for label in [
        "mfa.authenticator",
        "oauth2_provider.accesstoken",
        "sessions.session",
    ]:
        with pytest.raises(PermissionDenied):
            services.records(manager, "list", label)
    users = services.records(manager, "list", "users.user")
    assert all("password" not in row["fields"] for row in users["results"])


def test_unprivileged_staff_cannot_mutate_content(manager):
    user = UserFactory(is_staff=True)
    with pytest.raises(PermissionDenied):
        cms.pages(user, "create", values={"title": "Denied"})
    with pytest.raises(PermissionDenied):
        cms.plugins(
            user,
            "delete",
            home().pk,
            "hero",
            plugin_id=home()
            .get_placeholders()
            .get(slot="hero")
            .get_plugins()
            .first()
            .pk,
        )
    with pytest.raises(PermissionDenied):
        services.records(user, "create", "auth.group", values={"name": "Denied"})


@pytest.mark.parametrize("kind", ["file", "image"])
def test_chunk_upload_to_filer_and_metadata(manager, settings, tmp_path, kind):
    settings.MCP_UPLOAD_ROOT = tmp_path / "staging"
    settings.MEDIA_ROOT = tmp_path / "media"
    if kind == "image":
        stream = BytesIO()
        Image.new("RGB", (8, 8), "blue").save(stream, "PNG")
        data, name = stream.getvalue(), "sample.png"
    else:
        data, name = b"launcher bytes", "launcher.exe"
    state = media.uploads(
        manager,
        "begin",
        filename=name,
        size=len(data),
        kind=kind,
        sha256=hashlib.sha256(data).hexdigest(),
    )
    upload_id = state["upload_id"]
    cut = len(data) // 2
    for offset, chunk in [(0, data[:cut]), (cut, data[cut:])]:
        media.uploads(
            manager,
            "chunk",
            upload_id=upload_id,
            chunk=base64.b64encode(chunk).decode(),
            offset=offset,
        )
    result = media.uploads(manager, "finish", upload_id=upload_id)
    assert result["kind"] == kind
    assert result["filename"] == name
    asset = File.objects.get(pk=result["id"])
    assert asset.file.read() == data
    assert not list(settings.MCP_UPLOAD_ROOT.iterdir())
    media.media(manager, "delete", file_id=asset.pk)


def test_upload_ownership_offsets_and_mime_validation(manager, settings, tmp_path):
    settings.MCP_UPLOAD_ROOT = tmp_path
    state = media.uploads(manager, "begin", filename="bad.html", size=4)
    with pytest.raises(Upload.DoesNotExist):
        media.uploads(
            UserFactory(is_superuser=True, is_staff=True),
            "chunk",
            upload_id=state["upload_id"],
            offset=0,
            chunk="YWJjZA==",
        )
    with pytest.raises(ValidationError):
        media.uploads(
            manager,
            "chunk",
            upload_id=state["upload_id"],
            offset=2,
            chunk="YWJjZA==",
        )
    media.uploads(
        manager,
        "chunk",
        upload_id=state["upload_id"],
        offset=0,
        chunk="YWJjZA==",
    )
    with pytest.raises(ValidationError):
        media.uploads(manager, "finish", upload_id=state["upload_id"])
    media.uploads(manager, "abort", upload_id=state["upload_id"])
