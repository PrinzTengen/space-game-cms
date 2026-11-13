"""Initial gallery images from the former landing-page template."""

from cms.api import add_plugin
from cms.plugin_pool import plugin_pool

DEFAULT_IMAGES = (
    {
        "default_image": "meridian",
        "image_alt": "Meridian station near a planet",
        "title": "Meridian / Low orbit",
    },
    {
        "default_image": "maerzbach",
        "image_alt": "The Märzbach ship in front of a sunlit nebula",
        "title": "Märzbach / Solar drift",
    },
)


def add_default_gallery(content):
    placeholder = content.get_placeholders().get(slot="gallery")
    plugin = plugin_pool.get_plugin("SpaceGameGalleryPlugin")
    defaults = plugin.model().initialize_from_form(plugin.form).config
    group = add_plugin(
        placeholder,
        "SpaceGameGalleryPlugin",
        content.language,
        config=defaults,
    )
    for config in DEFAULT_IMAGES:
        add_plugin(
            placeholder,
            "SpaceGameGalleryImagePlugin",
            content.language,
            target=group,
            config=dict(config),
        )
    return group
