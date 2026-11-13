"""Public website copy and application state for the F2 Orbit theme."""

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialApp
from django.conf import settings

from space_game.theme.design import catalog
from space_game.theme.design import language


def design_system(request):
    if (
        request.path.startswith(f"/{settings.ADMIN_URL}")
        and "/cms/placeholder/object/" not in request.path
    ):
        return {}
    lang = language()
    data = catalog()
    strings = data["strings"][lang]
    nav = [
        {"url": url, "label": strings["nav"][key]}
        for key, url in [
            ("home", "/"),
            ("blog", "/stories/"),
            ("download", "/download/"),
            ("faq", "/faq/"),
        ]
    ]
    for item in nav:
        item["active"] = (
            request.path == item["url"]
            if item["url"] == "/"
            else request.path.startswith(item["url"])
        )
    discord_user = (
        request.user.is_authenticated
        and SocialAccount.objects.filter(
            user=request.user,
            provider="discord",
        ).exists()
    )
    discord_ready = (
        bool(settings.SG_DISCORD_CLIENT_ID and settings.SG_DISCORD_CLIENT_SECRET)
        or SocialApp.objects.filter(
            provider="discord",
            sites=settings.SITE_ID,
        ).exists()
    )
    platform = request.GET.get("platform", "win")
    if platform not in {"win", "linux"}:
        platform = "win"
    platforms = [
        {**entry, "active": entry["key"] == platform} for entry in data["platforms"]
    ]
    selected = next(p for p in platforms if p["active"])
    return {
        "sg": {
            "t": strings,
            "lang": lang,
            "nav": nav,
            "requirements": [
                {
                    key: value.get(lang, "") if isinstance(value, dict) else value
                    for key, value in row.items()
                }
                for row in data["requirements"]
            ],
            "faq": data["faq"][lang],
            "discord_ready": discord_ready,
            "discord_user": discord_user,
            "platforms": platforms,
            "file": selected,
            "install": strings["dl"]["install"][platform],
            "download_ready": bool(settings.SG_LAUNCHER_URLS.get(platform)),
        },
    }
