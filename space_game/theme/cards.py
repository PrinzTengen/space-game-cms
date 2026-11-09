"""Initial card content from the former landing-page template."""

from cms.api import add_plugin
from cms.plugin_pool import plugin_pool

DEFAULT_CARDS = (
    {
        "eyebrow": "01 / Resources",
        "title": "Make your own way.",
        "description": (
            "Explore the asteroid belt and discover what lies beyond "
            "the familiar routes."
        ),
        "default_image": "resources",
        "image_alt": "An asteroid belt in deep space",
    },
    {
        "eyebrow": "02 / Trade",
        "title": "Connect distant worlds.",
        "description": (
            "From one station to the next, every journey opens a new perspective."
        ),
        "default_image": "trade",
        "image_alt": "Levante station among the stars",
    },
    {
        "eyebrow": "03 / Exploration",
        "title": "Follow your curiosity.",
        "description": (
            "Set a course for Sky City and see the universe from a different angle."
        ),
        "default_image": "exploration",
        "image_alt": "Sky City space station",
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
