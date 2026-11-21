"""Initial card content from the former landing-page template."""

from cms.plugin_pool import plugin_pool

from space_game.theme.buttons import add_plugin

DEFAULT_CARDS = (
    {
        "eyebrow": "",
        "title": "Explore",
        "description": (
            "Jump into systems nobody has charted yet. "
            "Every scan fills in your star map."
        ),
    },
    {
        "eyebrow": "",
        "title": "Mine",
        "description": (
            "Analyse asteroids before you drill. Every rock has its own composition."
        ),
    },
    {
        "eyebrow": "",
        "title": "Trade",
        "description": (
            "Stations need different things. Know the routes and prices, "
            "and you earn the most."
        ),
    },
)


def add_default_cards(content):
    placeholder = content.get_placeholders().get(slot="discovery")
    plugin = plugin_pool.get_plugin("SpaceGameCardsPlugin")
    defaults = plugin.model().initialize_from_form(plugin.form).config
    group = add_plugin(
        placeholder,
        "SpaceGameCardsPlugin",
        content.language,
        config=defaults,
    )
    for config in DEFAULT_CARDS:
        add_plugin(
            placeholder,
            "SpaceGameCardPlugin",
            content.language,
            target=group,
            config=dict(config),
        )
    return group
