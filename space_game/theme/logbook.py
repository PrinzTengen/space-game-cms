"""Create an editable header in the native Stories apphook page."""

from cms.api import add_plugin
from cms.utils.placeholder import rescan_placeholders_for_obj

from space_game.theme.design import catalog


def add_default_logbook_header(content):
    strings = catalog()["strings"][content.language]["blog"]
    return add_plugin(
        rescan_placeholders_for_obj(content)["logbook_header"],
        "SpaceGameLogbookHeaderPlugin",
        content.language,
        config={
            "eyebrow": strings["label"],
            "title": strings["title"],
            "subtitle": strings["lead"],
        },
    )
