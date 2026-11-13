"""Compare frontend content before publishing an automatically created draft."""

from djangocms_frontend.models import FrontendUIItem
from djangocms_stories.models import LatestPostsPlugin


def frontend_snapshot(content):
    snapshot = {}
    for placeholder in content.placeholders.all():
        plugins = list(placeholder.get_plugins().order_by("position", "pk"))
        positions = {plugin.pk: index for index, plugin in enumerate(plugins)}
        rows = []
        for plugin in plugins:
            instance, _ = plugin.get_plugin_instance()
            if isinstance(instance, FrontendUIItem):
                config = (instance.ui_item, instance.tag_type, instance.config)
            elif isinstance(instance, LatestPostsPlugin):
                config = (
                    instance.app_config_id,
                    instance.latest_posts,
                    instance.current_site,
                    instance.template_folder,
                    tuple(instance.tags.order_by("pk").values_list("pk", flat=True)),
                    tuple(
                        instance.categories.order_by("pk").values_list("pk", flat=True),
                    ),
                )
            else:
                return None
            rows.append(
                (
                    plugin.plugin_type,
                    plugin.language,
                    positions.get(plugin.parent_id),
                    config,
                ),
            )
        snapshot[placeholder.slot] = rows
    return snapshot


def unchanged_frontend_draft(published, draft):
    same_fields = all(
        getattr(published, field.attname) == getattr(draft, field.attname)
        for field in published._meta.concrete_fields  # noqa: SLF001
        if not field.primary_key and field.name not in {"creation_date", "changed_date"}
    )
    original = frontend_snapshot(published)
    return same_fields and original is not None and original == frontend_snapshot(draft)
