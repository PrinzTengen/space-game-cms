"""Editable download content and published launcher destinations."""

from cms.api import add_plugin
from cms.models import PageContent
from cms.models import Placeholder
from cms.utils.placeholder import rescan_placeholders_for_obj
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from space_game.theme.design import catalog
from space_game.theme.design import language

DOWNLOAD_PLUGIN_TYPES = (
    "SpaceGameDownloadHeaderPlugin",
    "SpaceGameDownloadStepsPlugin",
    "SpaceGameDownloadStepPlugin",
    "SpaceGameLauncherPlugin",
    "SpaceGameLauncherPlatformPlugin",
    "SpaceGameDownloadInfoPlugin",
)


def launcher_url(config):
    destination = config.get("download_url") or settings.SG_LAUNCHER_URLS.get(
        config.get("platform"),
        "",
    )
    try:
        URLValidator(schemes=["https"])(destination)
    except ValidationError:
        return ""
    return destination


def published_launcher_url(platform, lang=None):
    if platform not in {"win", "linux"}:
        return ""
    pages = PageContent.objects.filter(
        page__reverse_id="download",
        page__site_id=settings.SITE_ID,
    )
    content = pages.filter(language=lang or language()).first()
    content = content or pages.filter(language="en").first()
    if content is None:
        return launcher_url({"platform": platform})
    for placeholder in content.placeholders.all():
        for plugin in (
            placeholder.get_plugins()
            .filter(
                plugin_type="SpaceGameLauncherPlatformPlugin",
                parent__plugin_type="SpaceGameLauncherPlugin",
                language=content.language,
            )
            .order_by("position")
        ):
            instance = plugin.get_plugin_instance()[0]
            if instance.config.get("platform") == platform:
                return launcher_url(instance.config)
    return ""


def add_default_download_plugins(content):
    data = catalog()
    strings = data["strings"][content.language]["dl"]
    scanned = rescan_placeholders_for_obj(content)
    # CMS marks newly scanned placeholders as empty in its prefetch cache.
    # Reload them so successive root plugins receive distinct positions.
    fresh = Placeholder.objects.in_bulk(p.pk for p in scanned.values())
    placeholders = {slot: fresh[p.pk] for slot, p in scanned.items()}
    lang = content.language
    add_plugin(
        placeholders["download_header"],
        "SpaceGameDownloadHeaderPlugin",
        lang,
        config={
            "eyebrow": strings["label"],
            "title": strings["title"],
            "subtitle": strings["lead"],
        },
    )
    steps = add_plugin(
        placeholders["download_steps"],
        "SpaceGameDownloadStepsPlugin",
        lang,
        config={"title": strings["stepsLabel"]},
    )
    for step in strings["steps"]:
        add_plugin(
            steps.placeholder,
            "SpaceGameDownloadStepPlugin",
            lang,
            target=steps,
            config={"title": step["title"], "description": step["description"]},
        )
    launcher = add_plugin(
        placeholders["launcher"],
        "SpaceGameLauncherPlugin",
        lang,
        config={
            "title": strings["osTitle"],
            "platform_label": strings["osLabel"],
            "file_label": strings["file"],
            "size_label": strings["size"],
            "version_label": strings["version"],
            "checksum_label": strings["sha"],
            "download_label": strings["dlBtn"],
            "install_label": strings["installLabel"],
            "unavailable_text": strings["unavailable"],
        },
    )
    for platform in data["platforms"]:
        add_plugin(
            launcher.placeholder,
            "SpaceGameLauncherPlatformPlugin",
            lang,
            target=launcher,
            config={
                "platform": platform["key"],
                "title": platform["label"],
                "description": platform["sub"],
                "download_url": "",
                "filename": platform["file"],
                "size": "",
                "version": "",
                "checksum": "",
                "instructions": strings["install"][platform["key"]],
            },
        )
    for config in [
        {
            "title": strings["communityTitle"],
            "description": strings["communityText"],
            "items": "\n".join(strings["communityItems"]),
            "button_label": strings["communityButton"],
            "button_link": {"external_link": "https://discord.gg/TeGQrqprRM"},
        },
        {
            "title": strings["reqTitle"],
            "description": strings["reqText"],
            "items": "",
            "button_label": strings["reqBtn"],
            "button_link": {"external_link": "/faq/"},
        },
    ]:
        add_plugin(
            placeholders["download_sidebar"],
            "SpaceGameDownloadInfoPlugin",
            lang,
            config=config,
        )
