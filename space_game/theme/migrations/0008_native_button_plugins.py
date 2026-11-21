"""Preserve existing buttons as native Link / Button children in every version."""

from django.db import migrations


def migrate_buttons(apps, schema_editor):
    item_model = apps.get_model("djangocms_frontend", "FrontendUIItem")
    plugin_model = apps.get_model("cms", "CMSPlugin")
    alias = schema_editor.connection.alias
    items = item_model.objects.using(alias)
    plugins = plugin_model.objects.using(alias)
    fields = {
        "SpaceGameHeroPlugin": [
            ("primary_label", "primary_link", "primary"),
            ("secondary_label", "secondary_link", "secondary"),
        ],
        "SpaceGameCTAPlugin": [("button_label", "button_link", "primary")],
        "SpaceGameDownloadInfoPlugin": [("button_label", "button_link", "secondary")],
        "SpaceGameCardPlugin": [("link_label", "link", "link")],
        "SpaceGameLauncherPlatformPlugin": [],
    }
    for instance in items.filter(plugin_type__in=fields).order_by("pk"):
        config = instance.config.copy()
        buttons = []
        for label_key, link_key, context in fields[instance.plugin_type]:
            label = config.pop(label_key, "")
            destination = config.pop(link_key, None)
            if label and destination:
                buttons.append(
                    {
                        "name": label,
                        "link": destination,
                        "link_type": "link" if context == "link" else "btn",
                        "link_context": "primary" if context == "link" else context,
                    }
                )
        if instance.plugin_type == "SpaceGameLauncherPlatformPlugin" and not config.get(
            "native_button"
        ):
            launcher = items.get(pk=instance.parent_id)
            label = launcher.config.get("download_label", "Download")
            buttons.append(
                {
                    "name": f"{label} · {config['title']}",
                    "link": {
                        "external_link": (
                            f"/launcher/{config['platform']}/?language={instance.language}"
                        )
                    },
                    "link_type": "btn",
                    "link_context": "primary",
                }
            )
            config["native_button"] = True
        if buttons:
            siblings = plugins.filter(
                placeholder_id=instance.placeholder_id,
                language=instance.language,
            )
            ordered = list(siblings.order_by("position"))
            descendants = {instance.pk}
            position = next(p.position for p in ordered if p.pk == instance.pk)
            for plugin in ordered:
                if plugin.parent_id in descendants:
                    descendants.add(plugin.pk)
                    position = max(position, plugin.position)
            # Descending updates also work with immediate uniqueness constraints.
            for plugin in siblings.filter(position__gt=position).order_by("-position"):
                plugins.filter(pk=plugin.pk).update(
                    position=plugin.position + len(buttons)
                )
            for offset, button in enumerate(buttons, start=1):
                items.create(
                    placeholder_id=instance.placeholder_id,
                    language=instance.language,
                    parent_id=instance.pk,
                    position=position + offset,
                    plugin_type="TextLinkPlugin",
                    ui_item="Link",
                    tag_type="div",
                    config={
                        "template": "default",
                        "link_size": "",
                        "target": "",
                        **button,
                    },
                )
        if config != instance.config:
            items.filter(pk=instance.pk).update(config=config)


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0045_pageurl_site_unique_path"),
        ("theme", "0007_spacegamefaq_spacegamefaqitem_spacegamerequirement_and_more"),
    ]
    operations = [migrations.RunPython(migrate_buttons, migrations.RunPython.noop)]
