"""Public website copy and application state for the F2 Orbit theme."""

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
    return {
        "sg": {
            "t": strings,
            "lang": lang,
            "nav": nav,
        },
    }
