"""Editorial components backed by django CMS Frontend's JSON configuration."""

from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.image.fields import ImageFormField
from djangocms_link.fields import LinkFormField

from space_game.theme.downloads import launcher_url


@components.register
class SpaceGameDownloadHeader(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Download Header")
        module = "Space Game"
        render_template = "theme/components/logbook_header.html"
        allow_children = False

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    subtitle = forms.CharField(
        label=_("Subtitle"),
        required=False,
        widget=forms.Textarea,
    )


@components.register
class SpaceGameDownloadSteps(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Download Steps")
        module = "Space Game"
        render_template = "theme/components/download_steps.html"
        child_classes = ["SpaceGameDownloadStepPlugin"]

    title = forms.CharField(label=_("Accessible label"), max_length=250)


@components.register
class SpaceGameDownloadStep(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Download Step")
        module = "Space Game"
        render_template = "theme/components/download_step.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameDownloadStepsPlugin"]

    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        max_length=250,
    )


@components.register
class SpaceGameLauncher(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Launcher Downloads")
        module = "Space Game"
        render_template = "theme/components/launcher.html"
        child_classes = ["SpaceGameLauncherPlatformPlugin"]
        default_config = {
            "title": "Choose your platform",
            "platform_label": "Operating system",
            "file_label": "File",
            "size_label": "Size",
            "version_label": "Version",
            "checksum_label": "SHA-256",
            "download_label": "Download",
            "install_label": "Installation",
            "unavailable_text": (
                "The launcher will appear here once the file is available."
            ),
        }

    title = forms.CharField(label=_("Heading"), max_length=250)
    platform_label = forms.CharField(
        label=_("Platform selection label"),
        max_length=150,
    )
    file_label = forms.CharField(label=_("File label"), max_length=100)
    size_label = forms.CharField(label=_("File size label"), max_length=100)
    version_label = forms.CharField(label=_("Version label"), max_length=100)
    checksum_label = forms.CharField(label=_("Checksum label"), max_length=100)
    download_label = forms.CharField(label=_("Download button text"), max_length=100)
    install_label = forms.CharField(label=_("Installation label"), max_length=100)
    unavailable_text = forms.CharField(
        label=_("Unavailable message"),
        widget=forms.Textarea,
    )


@components.register
class SpaceGameLauncherPlatform(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Launcher Platform")
        module = "Space Game"
        render_template = "theme/components/launcher_platform.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameLauncherPlugin"]

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            context["launcher"] = instance.parent.get_plugin_instance()[0]
            context["launcher_available"] = bool(launcher_url(instance.config))
            return context

    platform = forms.ChoiceField(
        label=_("Platform"),
        choices=[("win", "Windows"), ("linux", "Linux")],
    )
    title = forms.CharField(label=_("Platform name"), max_length=100)
    description = forms.CharField(
        label=_("System / architecture"),
        required=False,
        max_length=250,
    )
    download_url = forms.URLField(
        label=_("Launcher download URL"),
        required=False,
        help_text=_(
            "HTTPS URL. Leave empty to use the environment URL for this platform.",
        ),
    )
    filename = forms.CharField(label=_("File name"), required=False, max_length=250)
    size = forms.CharField(label=_("File size"), required=False, max_length=100)
    version = forms.CharField(label=_("Version"), required=False, max_length=100)
    checksum = forms.RegexField(
        label=_("SHA-256 checksum"),
        regex=r"\A[0-9a-fA-F]{64}\Z",
        required=False,
        help_text=_("Optional: full 64-character SHA-256 checksum."),
    )
    instructions = forms.CharField(
        label=_("Installation instructions"),
        required=False,
        widget=forms.Textarea,
    )

    def clean_download_url(self):
        value = self.cleaned_data["download_url"]
        if value and not value.startswith("https://"):
            raise forms.ValidationError(_("Use an HTTPS download URL."))
        return value


@components.register
class SpaceGameDownloadInfo(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Download Info")
        module = "Space Game"
        render_template = "theme/components/download_info.html"
        allow_children = False

    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    items = forms.CharField(
        label=_("List items"),
        required=False,
        widget=forms.Textarea,
        help_text=_("One item per line."),
    )
    button_label = forms.CharField(
        label=_("Button text"),
        required=False,
        max_length=100,
    )
    button_link = LinkFormField(label=_("Button destination"), required=False)


@components.register
class SpaceGameLogbookHeader(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Logbook Header")
        module = "Space Game"
        render_template = "theme/components/logbook_header.html"
        allow_children = False
        default_config = {
            "eyebrow": "News & Devlogs",
            "title": "Logbook",
            "subtitle": "Announcements, patch notes and a look behind the scenes.",
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    subtitle = forms.CharField(
        label=_("Subtitle"),
        required=False,
        widget=forms.Textarea,
    )


@components.register
class SpaceGameHero(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Hero")
        module = "Space Game"
        render_template = "theme/components/hero.html"
        allow_children = False
        default_config = {
            "eyebrow": "Exploration · Trade · Mining",
            "title": "Chart the unknown.",
            "description": (
                "A calm, technical space game. Fly into uncharted systems, mine "
                "resources and trade them between stations – at your own pace."  # noqa: RUF001
            ),
            "image_alt": "A space station against a glowing nebula",
            "primary_label": "Download launcher",
            "primary_link": {"external_link": "/download/"},
            "secondary_label": "Read devlogs",
            "secondary_link": {"external_link": "/stories/?type=devlog"},
            "note": "Pre-Alpha for Windows & Linux · No account required",
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    note = forms.CharField(
        label=_("Note below buttons"),
        required=False,
        max_length=250,
    )
    image = ImageFormField(
        label=_("Background image"),
        required=False,
        help_text=_("Uses the F2 Orbit key art if no image is selected."),
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
            "eyebrow": "The game in three parts",
            "title": "Explore. Mine. Trade.",
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


@components.register
class SpaceGameCTA(CMSFrontendComponent):
    class Meta:
        name = _("Space Game CTA")
        module = "Space Game"
        render_template = "theme/components/cta.html"
        allow_children = False
        default_config = {
            "eyebrow": "",
            "title": "Ready for your first launch?",
            "description": (
                "Download the launcher for Windows or Linux. No account required."
            ),
            "button_label": "Go to download",
            "button_link": {"external_link": "/download/"},
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    button_label = forms.CharField(label=_("Button text"), max_length=100)
    button_link = LinkFormField(label=_("Button destination"))
    image = ImageFormField(label=_("Background image"), required=False)


@components.register
class SpaceGameGallery(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Gallery")
        module = "Space Game"
        render_template = "theme/components/gallery.html"
        allow_children = True
        child_classes = ["SpaceGameGalleryImagePlugin"]
        default_config = {
            "eyebrow": "From the universe",
            "title": "A glimpse beyond the horizon.",
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )


@components.register
class SpaceGameGalleryImage(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Gallery Image")
        module = "Space Game"
        render_template = "theme/components/gallery_image.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameGalleryPlugin"]
        default_config = {
            "default_image": "meridian",
            "image_alt": "Meridian station near a planet",
        }

    image = ImageFormField(label=_("Image"), required=False)
    default_image = forms.ChoiceField(
        label=_("Default image"),
        required=False,
        choices=[
            ("", _("No default image")),
            ("meridian", _("Meridian station")),
            ("maerzbach", _("Märzbach in a sunlit nebula")),
        ],
        help_text=_("Used when no image is selected from the media library."),
    )
    image_alt = forms.CharField(label=_("Image description"), max_length=250)
    title = forms.CharField(label=_("Caption"), required=False, max_length=250)

    def clean(self):
        data = super().clean()
        if not data.get("image") and not data.get("default_image"):
            self.add_error("image", _("Select an image or a default image."))
        return data
