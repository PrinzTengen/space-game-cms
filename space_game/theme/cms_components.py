"""Editorial components backed by django CMS Frontend's JSON configuration."""

from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.image.fields import ImageFormField
from djangocms_link.fields import LinkFormField


@components.register
class SpaceGameHero(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Hero")
        module = "Space Game"
        render_template = "theme/components/hero.html"
        allow_children = False
        default_config = {
            "eyebrow": "Space Game / In development",
            "title": "Your journey starts here.",
            "description": (
                "Head into the unknown. Discover distant stations, follow new "
                "trade routes and find your place among the stars."
            ),
            "image_alt": "A space station against a glowing nebula",
            "primary_label": "Join the community",
            "primary_link": {"external_link": "https://discord.gg/TeGQrqprRM"},
            "secondary_label": "Discover Space Game",
            "secondary_link": {"external_link": "#discover"},
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    image = ImageFormField(
        label=_("Background image"),
        required=False,
        help_text=_("Uses the original Space Game image if no image is selected."),
    )
    image_alt = forms.CharField(
        label=_("Image description"),
        required=False,
        max_length=250,
    )
    primary_label = forms.CharField(
        label=_("Primary button text"),
        required=False,
        max_length=100,
    )
    primary_link = LinkFormField(label=_("Primary button destination"), required=False)
    secondary_label = forms.CharField(
        label=_("Secondary button text"),
        required=False,
        max_length=100,
    )
    secondary_link = LinkFormField(
        label=_("Secondary button destination"),
        required=False,
    )


@components.register
class SpaceGameCards(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Cards")
        module = "Space Game"
        render_template = "theme/components/cards.html"
        allow_children = True
        child_classes = ["SpaceGameCardPlugin"]
        default_config = {
            "eyebrow": "Choose your course",
            "title": "A universe full of possibilities.",
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), required=False, max_length=250)


@components.register
class SpaceGameCard(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Card")
        module = "Space Game"
        render_template = "theme/components/card.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameCardsPlugin"]

    title = forms.CharField(label=_("Heading"), max_length=250)
    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    image = ImageFormField(label=_("Image"), required=False)
    image_alt = forms.CharField(
        label=_("Image description"),
        required=False,
        max_length=250,
    )
    default_image = forms.ChoiceField(
        label=_("Default image"),
        required=False,
        choices=[
            ("", _("No image")),
            ("resources", _("Asteroid belt")),
            ("trade", _("Levante station")),
            ("exploration", _("Sky City")),
        ],
        help_text=_("Used when no image is selected from the media library."),
    )
    link_label = forms.CharField(
        label=_("Link text"),
        required=False,
        max_length=100,
    )
    link = LinkFormField(label=_("Link destination"), required=False)
