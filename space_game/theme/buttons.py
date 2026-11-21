"""Create native frontend links from the former component button fields."""

from cms.api import add_plugin as cms_add_plugin
from django.db import transaction
from django.urls import reverse

BUTTON_FIELDS = {
    "SpaceGameHeroPlugin": [
        ("primary_label", "primary_link", "primary"),
        ("secondary_label", "secondary_link", "secondary"),
    ],
    "SpaceGameCTAPlugin": [("button_label", "button_link", "primary")],
    "SpaceGameDownloadInfoPlugin": [("button_label", "button_link", "secondary")],
    "SpaceGameCardPlugin": [("link_label", "link", "link")],
    "SpaceGameLauncherPlatformPlugin": [],
}


@transaction.atomic
def convert_buttons(instance):
    """Consume legacy fields once, retaining order and existing child plugins."""
    fields = BUTTON_FIELDS.get(instance.plugin_type, [])
    config = instance.config.copy()
    if instance.plugin_type == "SpaceGameLauncherPlatformPlugin" and not config.get(
        "native_button",
    ):
        launcher = instance.parent.get_plugin_instance()[0]
        label = launcher.config.get("download_label", "Download")
        cms_add_plugin(
            instance.placeholder,
            "TextLinkPlugin",
            instance.language,
            target=instance,
            config={
                "name": f"{label} · {config['title']}",
                "link": {
                    "external_link": (
                        f"{reverse('launcher-download', args=[config['platform']])}"
                        f"?language={instance.language}"
                    ),
                },
                "template": "default",
                "link_type": "btn",
                "link_context": "primary",
                "link_size": "",
                "target": "",
            },
        )
        config["native_button"] = True
    for label_key, link_key, context in fields:
        label = config.pop(label_key, "")
        destination = config.pop(link_key, None)
        if label and destination:
            cms_add_plugin(
                instance.placeholder,
                "TextLinkPlugin",
                instance.language,
                target=instance,
                config={
                    "name": label,
                    "link": destination,
                    "template": "default",
                    "link_type": "link" if context == "link" else "btn",
                    "link_context": "primary" if context == "link" else context,
                    "link_size": "",
                    "target": "",
                },
            )
    if config != instance.config:
        instance.config = config
        instance.save(update_fields=["config"])


def add_plugin(*args, **kwargs):
    """Seed components with editable Link / Button children."""
    with transaction.atomic():
        instance = cms_add_plugin(*args, **kwargs)
        convert_buttons(instance)
        return instance
