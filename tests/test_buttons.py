"""Native child links, design-system rendering and legacy data conversion."""

from importlib import import_module
from types import SimpleNamespace

import pytest
from cms.api import add_plugin
from cms.models import Placeholder
from cms.plugin_pool import plugin_pool
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.template.loader import render_to_string
from djangocms_frontend.contrib.link.models import Link

from space_game.theme.buttons import BUTTON_FIELDS
from space_game.theme.buttons import convert_buttons

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("plugin_type", BUTTON_FIELDS)
def test_button_components_accept_native_links(plugin_type):
    plugin = plugin_pool.get_plugin(plugin_type)
    assert plugin.allow_children
    assert plugin.child_classes == ["TextLinkPlugin"]
    assert not {"primary_link", "secondary_link", "button_link", "link_label"} & set(
        plugin.form.base_fields,
    )


@pytest.mark.parametrize("outline", [False, True])
def test_native_button_preserves_target_icons_attributes_and_escaping(outline):
    instance = Link(
        config={
            "name": "Launch <One>",
            "link_type": "btn",
            "link_context": "primary",
            "link_outline": outline,
            "target": "_blank",
            "icon_right": "bi bi-arrow-right",
            "attributes": {"aria-label": "Launch safely"},
        },
    )
    html = render_to_string(
        "djangocms_frontend/bootstrap5/link/default/link.html",
        {"instance": instance, "mixin_link": "https://example.com/?a=1&b=2"},
    )
    assert 'target="_blank" rel="noopener noreferrer"' in html
    assert 'aria-label="Launch safely"' in html
    assert "Launch &lt;One&gt;" in html
    assert "bi bi-arrow-right" in html
    assert ("btn-galaxy" in html) is not outline


def test_legacy_migration_keeps_tree_positions_and_is_idempotent():
    placeholder = Placeholder.objects.create(slot="buttons")
    hero = add_plugin(
        placeholder,
        "SpaceGameHeroPlugin",
        "en",
        config={
            "title": "Custom hero",
            "primary_label": "About <us>",
            "primary_link": {"external_link": "/about/"},
            "secondary_label": "",
            "secondary_link": {},
        },
    )
    existing = add_plugin(
        placeholder,
        "TextLinkPlugin",
        "en",
        target=hero,
        config={
            "name": "Existing child",
            "link": {"external_link": "/existing/"},
        },
    )
    following = add_plugin(
        placeholder,
        "SpaceGameCTAPlugin",
        "en",
        config={
            "title": "Custom CTA",
            "button_label": "Contact",
            "button_link": {"external_link": "mailto:hello@example.com"},
        },
    )
    migration = import_module("space_game.theme.migrations.0008_native_button_plugins")
    state = MigrationExecutor(connection).loader.project_state(
        [
            ("theme", "0008_native_button_plugins"),
        ],
    )
    migration.migrate_buttons(state.apps, SimpleNamespace(connection=connection))
    rows = list(placeholder.get_plugins().order_by("position"))
    assert [p.plugin_type for p in rows] == [
        "SpaceGameHeroPlugin",
        "TextLinkPlugin",
        "TextLinkPlugin",
        "SpaceGameCTAPlugin",
        "TextLinkPlugin",
    ]
    assert rows[1].pk == existing.pk
    assert rows[2].parent_id == hero.pk
    assert rows[4].parent_id == following.pk
    assert [p.position for p in rows] == list(range(1, 6))
    hero.refresh_from_db()
    assert hero.config == {"title": "Custom hero"}
    button = rows[2].get_plugin_instance()[0]
    assert button.config["name"] == "About <us>"
    assert button.get_link() == "/about/"
    migration.migrate_buttons(state.apps, SimpleNamespace(connection=connection))
    convert_buttons(hero)
    assert placeholder.get_plugins().count() == len(rows)
