"""Install the native djangocms-stories latest entries plugin."""

from cms.api import add_plugin
from cms.utils.placeholder import rescan_placeholders_for_obj
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.cms_appconfig import config_defaults


def add_default_latest_posts(content):
    app_config, _ = StoriesConfig.objects.get_or_create(
        namespace="stories",
        defaults={"type": "StoriesApp", **config_defaults},
    )
    return add_plugin(
        rescan_placeholders_for_obj(content)["latest"],
        "BlogLatestEntriesPlugin",
        content.language,
        app_config=app_config,
        latest_posts=3,
        template_folder="plugins",
        current_site=True,
    )
