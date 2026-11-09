"""Create a frontend Hero using its editorial defaults."""

from cms.api import add_plugin
from cms.plugin_pool import plugin_pool


def add_default_hero(content):
    placeholder = content.get_placeholders().get(slot="hero")
    plugin = plugin_pool.get_plugin("SpaceGameHeroPlugin")
    instance = plugin.model().initialize_from_form(plugin.form)
    return add_plugin(
        placeholder,
        "SpaceGameHeroPlugin",
        content.language,
        config=instance.config,
    )
