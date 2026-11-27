"""Footer as static alias with slot-based, editable links."""

import re
from http import HTTPStatus

import pytest
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from cms.toolbar.utils import get_object_edit_url
from cms.utils.placeholder import get_placeholder_conf
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_alias.models import AliasContent
from djangocms_versioning.models import Version

from space_game.theme.design import catalog
from space_game.theme.footer import add_default_footer
from space_game.theme.footer import footer_alias
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def site_user():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def footer_html(client, lang="en"):
    response = client.get("/", HTTP_ACCEPT_LANGUAGE=lang)
    assert response.status_code == HTTPStatus.OK
    html = " ".join(response.content.decode().split())
    return html[html.index('<footer class="site-footer">') :]


def published(lang):
    return AliasContent.objects.get(alias=footer_alias(), language=lang)


def test_footer_placeholder_and_slots_only_take_their_plugins():
    assert get_placeholder_conf("plugins", "footer") == ["SpaceGameFooterPlugin"]
    assert get_placeholder_conf("limits", "footer") == {"SpaceGameFooterPlugin": 1}
    for slot in ("Pages", "Community", "Legal"):
        plugin = plugin_pool.get_plugin(f"SpaceGameFooter{slot}Plugin")
        assert plugin.child_classes == ["TextLinkPlugin"]
        assert plugin.parent_classes == ["SpaceGameFooterPlugin"]


def test_install_publishes_footer_with_links_in_their_slots(site_user, client):
    call_command("install_footer", username=site_user.username)
    html = footer_html(client)
    pages = html[html.index("sg-footer-pages") : html.index("sg-footer-community")]
    assert re.search(r'<li> ?<a href="/"[^>]*> ?<span>Home</span>', pages)
    assert 'href="/stories/"' in pages
    community = html[html.index("sg-footer-community") : html.index("sg-footer-bottom")]
    assert 'href="https://discord.gg/TeGQrqprRM"' in community
    assert "YouTube" not in html
    assert "Twitch" not in html  # No URL configured.
    bottom = html[html.index("sg-footer-bottom") :]
    assert "© 2026 Space Game · Pre-Alpha" in bottom
    assert "CookieLove.openSettings()" in bottom
    assert 'aria-label="Legal"' in bottom


def test_footer_is_translated_per_language(site_user, client):
    call_command("install_footer", username=site_user.username)
    strings = catalog()["strings"]["de"]
    html = footer_html(client, "de")
    assert strings["foot"]["line"] in html
    assert f'aria-label="{strings["foot"]["legal"]}"' in html
    assert f"<span>{strings['nav']['blog']}</span>" in html


def test_twitch_link_is_seeded_from_settings(site_user, client, settings):
    settings.SG_TWITCH_URL = "https://www.twitch.tv/example"
    call_command("install_footer", username=site_user.username)
    html = footer_html(client)
    community = html[html.index("sg-footer-community") : html.index("sg-footer-bottom")]
    assert 'href="https://www.twitch.tv/example"' in community


def test_install_is_idempotent(site_user):
    call_command("install_footer", username=site_user.username)
    count = Version.objects.count()
    call_command("install_footer", username=site_user.username)
    assert Version.objects.count() == count


def test_edits_are_published_separately_from_pages(site_user, client):
    call_command("install_footer", username=site_user.username)
    draft = Version.objects.get_for_content(published("en")).copy(site_user)
    footer = draft.content.placeholder.get_plugins().get(parent__isnull=True)
    instance = footer.get_plugin_instance()[0]
    instance.config["tagline"] = "Fly <safe>"
    instance.save()
    assert "Fly &lt;safe&gt;" not in footer_html(client)
    draft.publish(site_user)
    assert "Fly &lt;safe&gt;" in footer_html(client)


def test_empty_published_footer_shows_template_fallback(site_user, client):
    call_command("install_footer", username=site_user.username)
    draft = Version.objects.get_for_content(published("en")).copy(site_user)
    draft.content.placeholder.get_plugins().delete()
    draft.publish(site_user)
    html = footer_html(client)
    assert 'href="/faq/"' in html
    assert "CookieLove.openSettings()" in html


def test_fallback_is_shown_until_the_footer_is_published(site_user, client):
    html = footer_html(client)
    assert 'href="/download/"' in html
    assert "CookieLove.openSettings()" in html


def test_install_keeps_unpublished_editorial_draft(site_user):
    content = AliasContent.objects.with_user(site_user).create(
        alias=footer_alias(),
        name="footer",
        language="en",
    )
    add_default_footer(content, catalog()["strings"]["en"])
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_footer", username=site_user.username)


def test_footer_is_editable_on_pages_with_empty_slots(site_user, client):
    call_command("install_footer", username=site_user.username)
    draft = Version.objects.get_for_content(published("en")).copy(site_user)
    legal = draft.content.placeholder.get_plugins().get(
        plugin_type="SpaceGameFooterLegalPlugin",
    )
    home = PageContent.objects.get(page__is_home=True, language="en")
    page_draft = Version.objects.get_for_content(home).copy(site_user)
    client.force_login(site_user)
    response = client.get(get_object_edit_url(page_draft.content))
    assert response.status_code == HTTPStatus.OK
    html = response.content.decode()
    # Empty slots stay visible while editing so links can be added there.
    assert f"cms-plugin-{legal.pk}" in html
    assert "sg-footer-legal" in html


def test_footer_tree_positions_are_depth_first(site_user, settings):
    """Adding plugins to a slot in the editor requires a consistent tree."""
    settings.SG_TWITCH_URL = "https://www.twitch.tv/example"
    call_command("install_footer", username=site_user.username)
    plugins = list(published("en").placeholder.get_plugins().order_by("position"))
    children = {}
    for plugin in plugins:
        children.setdefault(plugin.parent_id, []).append(plugin)

    def walk(parent_id):
        for plugin in children.get(parent_id, []):
            yield plugin
            yield from walk(plugin.pk)

    assert [p.pk for p in walk(None)] == [p.pk for p in plugins]
    assert [p.position for p in plugins] == list(range(1, len(plugins) + 1))


def test_editor_can_add_a_link_to_each_slot(site_user, client):
    call_command("install_footer", username=site_user.username)
    draft = Version.objects.get_for_content(published("en")).copy(site_user)
    placeholder = draft.content.placeholder
    client.force_login(site_user)
    for slot_type in ("Pages", "Community", "Legal"):
        slot = placeholder.get_plugins().get(
            plugin_type=f"SpaceGameFooter{slot_type}Plugin",
        )
        position = placeholder.get_next_plugin_position(
            "en",
            parent=slot,
            insert_order="last",
        )
        response = client.get(
            reverse("admin:cms_placeholder_add_plugin"),
            {
                "placeholder_id": placeholder.pk,
                "plugin_type": "TextLinkPlugin",
                "plugin_language": "en",
                "plugin_parent": slot.pk,
                "plugin_position": position,
            },
        )
        assert response.status_code == HTTPStatus.OK, response.content[:300]
