"""Create a frontend Hero using its editorial defaults."""

from cms.plugin_pool import plugin_pool

from space_game.theme.buttons import add_plugin


def add_default_hero(content):
    placeholder = content.get_placeholders().get(slot="hero")
    plugin = plugin_pool.get_plugin("SpaceGameHeroPlugin")
    instance = plugin.model().initialize_from_form(plugin.form)
    instance.config.update(
        {
            "primary_label": "Download launcher",
            "primary_link": {"external_link": "/download/"},
            "secondary_label": "Read devlogs",
            "secondary_link": {"external_link": "/stories/?type=devlog"},
        },
    )
    return add_plugin(
        placeholder,
        "SpaceGameHeroPlugin",
        content.language,
        config=instance.config,
    )
