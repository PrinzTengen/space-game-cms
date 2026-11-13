"""Editable download modules, public URLs and version-safe migration."""

from http import HTTPStatus

import pytest
from cms.models import PageContent
from cms.toolbar.utils import get_object_edit_url
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils.html import escape
from djangocms_versioning.models import Version
from filer.models import File

from space_game.theme.cms_components import SpaceGameLauncherPlatform
from space_game.theme.downloads import DOWNLOAD_PLUGIN_TYPES
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def download_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    return user


def download_page(lang="en"):
    return PageContent.objects.get(page__reverse_id="download", language=lang)


def instances(content, slot):
    return [
        plugin.get_plugin_instance()[0]
        for plugin in content.get_placeholders()
        .get(slot=slot)
        .get_plugins()
        .order_by("position")
    ]


def windows(content):
    return next(
        p for p in instances(content, "launcher") if p.config.get("platform") == "win"
    )


@pytest.fixture
def uploaded_launcher(download_site, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    attached = File.objects.create(
        file=SimpleUploadedFile("real-launcher.exe", b"MZ" + b"upload-check" * 400),
        original_filename="real-launcher.exe",
        owner=download_site,
        is_public=True,
    )
    yield attached
    attached.file.delete(save=False)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_download_content_is_editable_plugins_in_both_languages(
    download_site,
    client,
    lang,
):
    content = download_page(lang)
    plugins = [
        p
        for placeholder in content.placeholders.all()
        for p in placeholder.get_plugins()
    ]
    assert {p.plugin_type for p in plugins} == set(DOWNLOAD_PLUGIN_TYPES)
    assert len(plugins) == 9  # noqa: PLR2004
    client.post(reverse("set_language"), {"language": lang, "next": "/download/"})
    response = client.get("/download/")
    assert response.status_code == HTTPStatus.OK
    for slot in ["download_header", "download_steps", "launcher", "download_sidebar"]:
        for instance in instances(content, slot):
            assert escape(instance.config["title"]).encode() in response.content
    assert b"/accounts/discord/login/" not in response.content
    assert b"sg-signin" not in response.content


def test_all_download_modules_have_native_edit_forms(download_site, client):
    draft = Version.objects.get_for_content(download_page()).copy(download_site)
    client.force_login(download_site)
    forms = [
        (
            instances(draft.content, "download_header")[0],
            ["title", "subtitle", "eyebrow"],
        ),
        (instances(draft.content, "download_steps")[1], ["title", "description"]),
        (
            instances(draft.content, "launcher")[0],
            ["title", "download_label", "unavailable_text"],
        ),
        (
            windows(draft.content),
            [
                "launcher_file",
                "download_url",
                "filename",
                "size",
                "version",
                "checksum",
                "instructions",
            ],
        ),
        (
            instances(draft.content, "download_sidebar")[0],
            ["title", "description", "items", "button_label"],
        ),
    ]
    for instance, fields in forms:
        response = client.get(
            reverse("admin:cms_placeholder_edit_plugin", args=[instance.pk]),
        )
        assert response.status_code == HTTPStatus.OK
        for field in fields:
            assert f'id="id_{field}"'.encode() in response.content
    response = client.get(get_object_edit_url(draft.content))
    assert response.status_code == HTTPStatus.OK
    assert b"data-launcher-edit-mode" in response.content
    assert b'data-launcher-platform="win"' in response.content
    assert b'data-launcher-platform="linux"' in response.content


def test_public_download_uses_published_plugin_url_without_login(
    download_site,
    client,
    settings,
):
    settings.SG_LAUNCHER_URLS = {"win": "https://example.com/old.exe"}
    draft = Version.objects.get_for_content(download_page()).copy(download_site)
    heading = instances(draft.content, "download_header")[0]
    heading.config.update(title="Get <the launcher>", subtitle="New & public")
    heading.save()
    platform = windows(draft.content)
    platform.config.update(
        download_url="https://example.com/new.exe",
        filename="new.exe",
        checksum="a" * 64,
    )
    platform.save()
    assert client.get("/launcher/win/?language=en").url == "https://example.com/old.exe"
    assert b"Get &lt;the launcher&gt;" not in client.get("/download/").content
    draft.publish(download_site)
    response = client.get("/download/")
    assert b"Get &lt;the launcher&gt;" in response.content
    assert b"New &amp; public" in response.content
    assert b"new.exe" in response.content
    assert ("a" * 64).encode() in response.content
    assert client.get("/launcher/win/?language=en").url == "https://example.com/new.exe"
    assert client.get("/launcher/win/?language=de").url == "https://example.com/old.exe"


def test_native_file_picker_saves_reference_and_published_file_is_public(
    uploaded_launcher,
    download_site,
    client,
    settings,
):
    settings.SG_LAUNCHER_URLS = {"win": "https://example.com/old.exe"}
    draft = Version.objects.get_for_content(download_page()).copy(download_site)
    platform = windows(draft.content)
    data = dict(platform.config)
    data.update(
        launcher_file=uploaded_launcher.pk,
        filename="obsolete-filename.exe",
        size="incorrect size",
        download_url="https://example.com/external.exe",
    )
    client.force_login(download_site)
    response = client.post(
        reverse("admin:cms_placeholder_edit_plugin", args=[platform.pk]),
        data={**data, "_save": "Save"},
    )
    assert response.status_code == HTTPStatus.OK
    platform.refresh_from_db()
    assert platform.config["launcher_file"] == {
        "model": "filer.file",
        "pk": uploaded_launcher.pk,
    }
    client.logout()
    assert client.get("/launcher/win/").url == "https://example.com/old.exe"
    draft.publish(download_site)
    response = client.get("/download/")
    assert b"real-launcher.exe" in response.content
    assert b"obsolete-filename.exe" not in response.content
    assert b"incorrect size" not in response.content
    response = client.get("/launcher/win/")
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "application/octet-stream"
    assert response["Content-Disposition"] == 'attachment; filename="real-launcher.exe"'
    assert b"".join(response.streaming_content) == b"MZ" + b"upload-check" * 400
    copy = Version.objects.get_for_content(download_page()).copy(download_site)
    assert (
        windows(copy.content).config["launcher_file"]
        == platform.config["launcher_file"]
    )
    client.force_login(download_site)
    response = client.get(
        reverse("admin:cms_placeholder_edit_plugin", args=[windows(copy.content).pk]),
    )
    assert response.status_code == HTTPStatus.OK
    assert b"real-launcher.exe" in response.content


def test_private_file_is_rejected_and_never_served_as_public_download(
    uploaded_launcher,
    client,
):
    File.objects.filter(pk=uploaded_launcher.pk).update(is_public=False)
    form = SpaceGameLauncherPlatform(
        data={
            "platform": "win",
            "title": "Windows",
            "launcher_file": uploaded_launcher.pk,
        },
    )
    assert not form.is_valid()
    assert "launcher_file" in form.errors
    platform = windows(download_page())
    platform.config["launcher_file"] = {
        "model": "filer.file",
        "pk": uploaded_launcher.pk,
    }
    platform.save()
    assert client.get("/launcher/win/").status_code == HTTPStatus.NOT_FOUND
    assert b"/launcher/win/" not in client.get("/download/").content


@pytest.mark.parametrize("missing", ["record", "bytes"])
def test_missing_attached_file_returns_404_without_falling_back_to_another_build(
    uploaded_launcher,
    client,
    missing,
):
    platform = windows(download_page())
    platform.config.update(
        launcher_file={"model": "filer.file", "pk": uploaded_launcher.pk},
        download_url="https://example.com/another-build.exe",
    )
    platform.save()
    if missing == "record":
        File.objects.filter(pk=uploaded_launcher.pk).delete()
    else:
        uploaded_launcher.file.storage.delete(uploaded_launcher.file.name)
    assert client.get("/launcher/win/").status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "url",
    ["http://example.com/file", "javascript:alert(1)", "https://"],
)
def test_unsafe_plugin_urls_are_rejected_by_form_and_route(download_site, client, url):
    form = SpaceGameLauncherPlatform(
        data={"platform": "win", "title": "Windows", "download_url": url},
    )
    assert not form.is_valid()
    assert "download_url" in form.errors
    # A malformed value imported directly into JSON must still be rejected.
    platform = windows(download_page())
    platform.config["download_url"] = url
    platform.save()
    assert client.get("/launcher/win/").status_code == HTTPStatus.NOT_FOUND
    assert b"/launcher/win/" not in client.get("/download/").content


def test_removing_plugins_does_not_restore_hardcoded_downloads(
    download_site,
    client,
    settings,
):
    settings.SG_LAUNCHER_URLS = {"win": "https://example.com/launcher.exe"}
    draft = Version.objects.get_for_content(download_page()).copy(download_site)
    for placeholder in draft.content.placeholders.all():
        placeholder.get_plugins().delete()
    draft.publish(download_site)
    response = client.get("/download/")
    assert b'class="sg-page-header"' not in response.content
    assert b"data-launcher-platform" not in response.content
    assert b'class="sg-stepper"' not in response.content
    assert client.get("/launcher/win/").status_code == HTTPStatus.NOT_FOUND


def test_download_installer_is_idempotent_and_keeps_editorial_changes(download_site):
    draft = Version.objects.get_for_content(download_page()).copy(download_site)
    instance = windows(draft.content)
    instance.config["download_url"] = "https://example.com/custom.exe"
    instance.save()
    count = Version.objects.count()
    call_command("install_download_plugins", username=download_site.username)
    assert Version.objects.count() == count
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert (
        windows(draft.content).config["download_url"]
        == "https://example.com/custom.exe"
    )


def legacy_page():
    content = download_page()
    content.placeholders.exclude(slot="content").delete()
    return content


def test_installer_converts_legacy_page_with_unchanged_draft(download_site):
    draft = Version.objects.get_for_content(legacy_page()).copy(download_site)
    call_command("install_download_plugins", username=download_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert windows(download_page()).config["title"] == "Windows"


def test_download_installer_protects_edited_legacy_draft(download_site):
    content = legacy_page()
    draft = Version.objects.get_for_content(content).copy(download_site)
    draft.content.title = "Not ready to publish"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished edited draft"):
        call_command("install_download_plugins", username=download_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Version.objects.get_for_content(content).state == "published"


def test_stock_login_copy_migration_keeps_custom_content(download_site):
    home = PageContent.objects.get(page__is_home=True, language="en")
    hero = instances(home, "hero")[0]
    hero.config.update(
        title="A custom hero",
        note="Pre-Alpha for Windows & Linux · Sign in with Discord",
    )
    hero.save()
    cta = instances(home, "community")[0]
    cta.config["description"] = "Custom community invitation"
    cta.save()
    call_command("install_download_plugins", username=download_site.username)
    home = PageContent.objects.get(page__is_home=True, language="en")
    assert instances(home, "hero")[0].config["title"] == "A custom hero"
    assert "No account required" in instances(home, "hero")[0].config["note"]
    assert (
        instances(home, "community")[0].config["description"]
        == "Custom community invitation"
    )
