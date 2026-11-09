"""Compare frontend content before publishing an automatically created draft."""

from djangocms_frontend.models import FrontendUIItem


def frontend_snapshot(content):
    snapshot = {}
    for placeholder in content.get_placeholders():
        plugins = list(placeholder.get_plugins().order_by("position", "pk"))
        positions = {plugin.pk: index for index, plugin in enumerate(plugins)}
        rows = []
        for plugin in plugins:
            instance, _ = plugin.get_plugin_instance()
            if not isinstance(instance, FrontendUIItem):
                return None
            rows.append(
                (
                    plugin.plugin_type,
                    plugin.language,
                    positions.get(plugin.parent_id),
                    instance.ui_item,
                    instance.tag_type,
                    instance.config,
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
