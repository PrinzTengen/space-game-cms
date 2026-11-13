"""Seed standalone FAQ and system requirements components from the source copy."""

from cms.api import add_plugin
from cms.models import Placeholder
from cms.utils.placeholder import rescan_placeholders_for_obj

from space_game.theme.design import catalog

FAQ_PLUGIN_TYPES = (
    "SpaceGameSupportHeaderPlugin",
    "SpaceGameFAQPlugin",
    "SpaceGameFAQItemPlugin",
    "SpaceGameRequirementsPlugin",
    "SpaceGameRequirementPlugin",
)


def add_default_faq_plugins(content):
    data = catalog()
    lang = content.language
    strings = data["strings"][lang]["faq"]
    scanned = rescan_placeholders_for_obj(content)
    fresh = Placeholder.objects.in_bulk(p.pk for p in scanned.values())
    placeholders = {slot: fresh[p.pk] for slot, p in scanned.items()}
    add_plugin(
        placeholders["support_header"],
        "SpaceGameSupportHeaderPlugin",
        lang,
        config={"eyebrow": strings["label"], "title": strings["title"], "subtitle": ""},
    )
    requirements = add_plugin(
        placeholders["system_requirements"],
        "SpaceGameRequirementsPlugin",
        lang,
        config={
            "title": strings["reqTitle"],
            "component_label": strings["comp"],
            "minimum_label": strings["min"],
            "recommended_label": strings["rec"],
            "note": strings["reqNote"],
        },
    )
    for row in data["requirements"]:
        values = {
            key: value.get(lang, "") if isinstance(value, dict) else value
            for key, value in row.items()
        }
        add_plugin(
            requirements.placeholder,
            "SpaceGameRequirementPlugin",
            lang,
            target=requirements,
            config={
                "title": values["l"],
                "minimum": values["min"],
                "recommended": values["rec"],
            },
        )
    faq = add_plugin(
        placeholders["faq"],
        "SpaceGameFAQPlugin",
        lang,
        config={"title": strings["faqTitle"], "description": "", "single_open": True},
    )
    for index, (question, answer) in enumerate(data["faq"][lang]):
        add_plugin(
            faq.placeholder,
            "SpaceGameFAQItemPlugin",
            lang,
            target=faq,
            config={
                "question": question,
                "answer": answer,
                "initially_open": index == 0,
            },
        )
