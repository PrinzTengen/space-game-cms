"""Editable apphook headers and safe, published-only search content."""

from http import HTTPStatus

import pytest
from cms.models import PageContent
from cms.toolbar.utils import get_object_edit_url
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.theme.templatetags.design_tags import post_search_text
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def logbook_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def logbook(language="en"):
    return PageContent.objects.get(page__reverse_id="stories", language=language)


def header(content):
    plugin = content.get_placeholders().get(slot="logbook_header").get_plugins().get()
    return plugin.get_plugin_instance()[0]


def test_bilingual_headers_are_stored_in_cms(client):
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    for lang, heading in [("en", "Logbook"), ("de", "Logbuch")]:
        content = logbook(lang)
        assert content.template == "cms/logbook.html"
        assert header(content).config["title"] == heading
        client.post(reverse("set_language"), {"language": lang, "next": "/stories/"})
        response = client.get("/stories/")
        assert response.status_code == HTTPStatus.OK
        assert f"<h1>{heading}</h1>".encode() in response.content
        assert b'id="logbook-search"' in response.content


def test_header_edit_dialog_and_page_editor(logbook_site, client):
    draft = Version.objects.get_for_content(logbook()).copy(logbook_site)
    client.force_login(logbook_site)
    response = client.get(
        reverse("admin:cms_placeholder_edit_plugin", args=[header(draft.content).pk]),
    )
    assert response.status_code == HTTPStatus.OK
    for field in ["eyebrow", "title", "subtitle"]:
        assert f'id="id_{field}"'.encode() in response.content
    response = client.get(get_object_edit_url(draft.content))
    assert response.status_code == HTTPStatus.OK
    assert b"<h1>Logbook</h1>" in response.content
    assert f"cms-plugin-{header(draft.content).pk}".encode() in response.content


def test_publishing_header_keeps_drafts_private_and_escapes_text(logbook_site, client):
    draft = Version.objects.get_for_content(logbook()).copy(logbook_site)
    instance = header(draft.content)
    instance.config.update(
        eyebrow="Mission updates",
        title="Our <Logbook>",
        subtitle='Development & "more" <script>alert(1)</script>',
    )
    instance.save()
    assert b"Our &lt;Logbook&gt;" not in client.get("/stories/").content
    draft.publish(logbook_site)
    response = client.get("/stories/")
    assert b"<h1>Our &lt;Logbook&gt;</h1>" in response.content
    assert b"Development &amp; &quot;more&quot; &lt;script&gt;" in response.content
    assert b"Mission updates" in response.content


def test_installer_upgrades_legacy_page_and_preserves_custom_header(logbook_site):
    content = logbook()
    content.get_placeholders().get(slot="logbook_header").delete()
    content.template = "cms/default.html"
    content.save()
    draft = Version.objects.get_for_content(content).copy(logbook_site)
    call_command("install_logbook_header", username=logbook_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert logbook().template == "cms/logbook.html"
    assert header(logbook()).config["title"] == "Logbook"
    instance = header(logbook())
    instance.config["title"] = "Custom editorial heading"
    instance.save()
    versions = Version.objects.count()
    call_command("install_logbook_header", username=logbook_site.username)
    assert Version.objects.count() == versions
    assert header(logbook()).config["title"] == "Custom editorial heading"


def test_installer_protects_edited_drafts(logbook_site):
    content = logbook()
    content.get_placeholders().get(slot="logbook_header").delete()
    draft = Version.objects.get_for_content(content).copy(logbook_site)
    draft.content.title = "An unfinished edit"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished edited draft"):
        call_command("install_logbook_header", username=logbook_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Version.objects.get_for_content(content).state == "published"
    assert not draft.content.placeholders.filter(slot="logbook_header").exists()


def test_search_contains_full_text_and_tags_without_leaking_drafts(
    logbook_site, client,
):
    post = Post.objects.create(
        author=logbook_site,
        app_config=StoriesConfig.objects.get(namespace="stories"),
    )
    post.tags.add("devlog", "Engineering")
    content = PostContent.objects.with_user(logbook_site).create(
        post=post,
        language="en",
        title="A published update",
        slug="a-published-update",
        subtitle="Devlog",
        abstract="Visible summary",
        post_text='<p>BodyOnlyMarker &amp; spaces</p><p>Next "paragraph".</p>',
    )
    assert "BodyOnlyMarker" not in client.get("/stories/").content.decode()
    Version.objects.get_for_content(content).publish(logbook_site)
    text = post_search_text(content)
    assert 'BodyOnlyMarker & spaces Next "paragraph".' in text
    assert "Engineering" in text
    response = client.get("/stories/")
    assert (
        b"BodyOnlyMarker &amp; spaces Next &quot;paragraph&quot;." in response.content
    )
    assert b"<p>BodyOnlyMarker" not in response.content
    draft = Version.objects.get_for_content(content).copy(logbook_site)
    draft.content.post_text = "SecretDraftMarker"
    draft.content.save()
    response = client.get("/stories/")
    assert b"BodyOnlyMarker" in response.content
    assert b"SecretDraftMarker" not in response.content
    assert b"BodyOnlyMarker" not in client.get("/").content
