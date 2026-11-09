"""Create a frontend call to action using its editorial defaults."""

from cms.api import add_plugin
from cms.plugin_pool import plugin_pool


def add_default_cta(content):
    placeholder = content.get_placeholders().get(slot="community")
    plugin = plugin_pool.get_plugin("SpaceGameCTAPlugin")
    instance = plugin.model().initialize_from_form(plugin.form)
    return add_plugin(
        placeholder,
        "SpaceGameCTAPlugin",
        content.language,
        config=instance.config,
    )
