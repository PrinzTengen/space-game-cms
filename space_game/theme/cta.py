"""Create a frontend call to action using its editorial defaults."""

from cms.plugin_pool import plugin_pool

from space_game.theme.buttons import add_plugin


def add_default_cta(content):
    placeholder = content.get_placeholders().get(slot="community")
    plugin = plugin_pool.get_plugin("SpaceGameCTAPlugin")
    instance = plugin.model().initialize_from_form(plugin.form)
    instance.config.update(
        {
            "button_label": "Go to download",
            "button_link": {"external_link": "/download/"},
        },
    )
    return add_plugin(
        placeholder,
        "SpaceGameCTAPlugin",
        content.language,
        config=instance.config,
    )
