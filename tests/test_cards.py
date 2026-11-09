"""Card components, editorial nesting and versioned installation."""

from http import HTTPStatus

import pytest
from cms.api import add_plugin
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_versioning.models import Version

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def card_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def homepage():
    return PageContent.objects.get(page__is_home=True, language="en")


def test_default_cards_are_saved_as_children(card_site, client):
    content = homepage()
    placeholder = content.get_placeholders().get(slot="discovery")
    group = placeholder.get_plugins().get(plugin_type="SpaceGameCardsPlugin")
    cards = list(group.get_children().order_by("position"))
    assert len(cards) == 3  # noqa: PLR2004
    assert {card.plugin_type for card in cards} == {"SpaceGameCardPlugin"}
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b'class="feature-card"') == 3  # noqa: PLR2004
    assert b"Make your own way." in response.content
    assert b"Connect distant worlds." in response.content
    assert b"Follow your curiosity." in response.content


@pytest.mark.parametrize("count", [1, 6, 7, 10])
def test_any_card_count_is_preserved_and_rendered(card_site, client, count):
    draft = Version.objects.get_for_content(homepage()).copy(card_site)
    placeholder = draft.content.get_placeholders().get(slot="discovery")
    group = placeholder.get_plugins().get(plugin_type="SpaceGameCardsPlugin")
    group.get_children().delete()
    for index in range(count):
        add_plugin(
            placeholder,
            "SpaceGameCardPlugin",
            "en",
            target=group,
            config={"title": f"Card {index + 1}"},
        )
    draft.publish(card_site)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b'class="feature-card"') == count
    assert f"Card {count}".encode() in response.content
    assert b"data-load-all-cards" in response.content


def test_card_nesting_and_edit_dialog(card_site, client):
    content = homepage()
    parent = plugin_pool.get_plugin("SpaceGameCardsPlugin")
    child = plugin_pool.get_plugin("SpaceGameCardPlugin")
    assert parent.get_child_classes("discovery", content) == [
        "SpaceGameCardPlugin",
    ]
    assert child.get_parent_classes("discovery", content) == [
        "SpaceGameCardsPlugin",
    ]
    assert child.require_parent is True
    draft = Version.objects.get_for_content(content).copy(card_site)
    card = (
        draft.content.get_placeholders()
        .get(slot="discovery")
        .get_plugins()
        .filter(
            plugin_type="SpaceGameCardPlugin",
        )
        .first()
    )
    client.force_login(card_site)
    response = client.get(reverse("admin:cms_placeholder_edit_plugin", args=[card.pk]))
    assert response.status_code == HTTPStatus.OK
    for name in [
        "title",
        "description",
        "image",
        "image_alt",
        "default_image",
        "link_label",
    ]:
        assert f'id="id_{name}"'.encode() in response.content


def test_install_cards_is_idempotent_and_preserves_hero(card_site):
    content = homepage()
    content.get_placeholders().get(slot="discovery").get_plugins().delete()
    draft = Version.objects.get_for_content(content).copy(card_site)
    call_command("install_home_cards", username=card_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert homepage().get_placeholders().get(slot="hero").get_plugins().count() == 1
    plugins = homepage().get_placeholders().get(slot="discovery").get_plugins()
    assert plugins.count() == 4  # noqa: PLR2004
    count = Version.objects.count()
    call_command("install_home_cards", username=card_site.username)
    assert Version.objects.count() == count


def test_install_cards_keeps_unpublished_hero_changes(card_site):
    content = homepage()
    content.get_placeholders().get(slot="discovery").get_plugins().delete()
    original = Version.objects.get_for_content(content)
    draft = original.copy(card_site)
    hero, _ = (
        draft.content.get_placeholders()
        .get(slot="hero")
        .get_plugins()
        .get()
        .get_plugin_instance()
    )
    hero.config["title"] = "An unpublished hero change"
    hero.save()
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_home_cards", username=card_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Version.objects.get(pk=original.pk).state == "published"
    hero.refresh_from_db()
    assert hero.config["title"] == "An unpublished hero change"
