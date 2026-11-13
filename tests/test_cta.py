"""CTA editing, versioned publishing and safe installation."""

from http import HTTPStatus

import pytest
from cms.models import Page
from cms.models import PageContent
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_frontend.models import FrontendUIItem
from djangocms_versioning.models import Version

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def cta_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def homepage():
    return PageContent.objects.get(page__is_home=True, language="en")


def cta_instance(content):
    plugin = content.get_placeholders().get(slot="community").get_plugins().get()
    return plugin.get_plugin_instance()[0]


def test_cta_is_saved_below_cards_and_editable(cta_site, client):
    content = homepage()
    instance = cta_instance(content)
    assert isinstance(instance, FrontendUIItem)
    assert instance.plugin_type == "SpaceGameCTAPlugin"
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    html = response.content.decode()
    assert html.index('class="feature-card sg-window"') < html.index(
        'class="space-callout"',
    )
    assert "Ready for your first launch?" in html
    assert "Go to download" in html
    draft = Version.objects.get_for_content(content).copy(cta_site)
    client.force_login(cta_site)
    response = client.get(
        reverse(
            "admin:cms_placeholder_edit_plugin",
            args=[cta_instance(draft.content).pk],
        ),
    )
    assert response.status_code == HTTPStatus.OK
    for field in ["eyebrow", "title", "description", "button_label", "image"]:
        assert f'id="id_{field}"'.encode() in response.content
    assert b"button_link" in response.content


def test_cta_copy_publish_and_internal_link(cta_site, client):
    draft = Version.objects.get_for_content(homepage()).copy(cta_site)
    instance = cta_instance(draft.content)
    about = Page.objects.get(reverse_id="about")
    instance.config.update(
        eyebrow="",
        title="Mission <One>",
        description="A new <community>",
        button_label="Join <One>",
        button_link={"internal_link": f"cms.page:{about.pk}"},
    )
    instance.save()
    assert b"Mission &lt;One&gt;" not in client.get("/").content
    draft.publish(cta_site)
    response = client.get("/")
    assert b"Mission &lt;One&gt;" in response.content
    assert b"A new &lt;community&gt;" in response.content
    assert b"Join &lt;One&gt;" in response.content
    html = " ".join(response.content.decode().split())
    assert 'href="/about/" rel="noopener">Join' in html
    assert b"Follow the development" not in response.content


def test_removing_cta_does_not_restore_template_fallback(cta_site, client):
    draft = Version.objects.get_for_content(homepage()).copy(cta_site)
    draft.content.get_placeholders().get(slot="community").get_plugins().delete()
    draft.publish(cta_site)
    assert b"space-callout" not in client.get("/").content


def test_install_cta_is_idempotent_and_keeps_other_plugins(cta_site):
    content = homepage()
    content.get_placeholders().get(slot="community").get_plugins().delete()
    draft = Version.objects.get_for_content(content).copy(cta_site)
    call_command("install_home_cta", username=cta_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert cta_instance(homepage()).config["title"] == "Ready for your first launch?"
    assert homepage().get_placeholders().get(slot="hero").get_plugins().count() == 1
    cards = homepage().get_placeholders().get(slot="discovery").get_plugins()
    assert cards.count() == 4  # noqa: PLR2004
    count = Version.objects.count()
    call_command("install_home_cta", username=cta_site.username)
    assert Version.objects.count() == count


def test_install_cta_preserves_unpublished_changes(cta_site):
    content = homepage()
    content.get_placeholders().get(slot="community").get_plugins().delete()
    original = Version.objects.get_for_content(content)
    draft = original.copy(cta_site)
    draft.content.title = "Unpublished home title"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_home_cta", username=cta_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Version.objects.get(pk=original.pk).state == "published"
    plugins = draft.content.get_placeholders().get(slot="community").get_plugins()
    assert not plugins.exists()
