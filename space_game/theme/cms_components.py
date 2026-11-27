"""Editorial components backed by django CMS Frontend's JSON configuration."""

from cms.models import PageContent
from cms.utils.plugins import get_plugins
from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.db.models import ManyToOneRel
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.image.fields import ImageFormField
from filer.fields.file import AdminFileFormField
from filer.fields.file import FilerFileField
from filer.models import File

from space_game.theme.design import language
from space_game.theme.downloads import launcher_file
from space_game.theme.downloads import launcher_url
from space_game.theme.seo import faq_schema_entry


@components.register
class SpaceGameSupportHeader(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Support Header")
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
class SpaceGameFAQ(CMSFrontendComponent):
    class Meta:
        name = _("Space Game FAQ")
        module = "Space Game"
        render_template = "theme/components/faq.html"
        child_classes = ["SpaceGameFAQItemPlugin"]
        default_config = {"title": "Frequently asked questions", "single_open": True}

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            context["faq_group"] = instance
            return context

    title = forms.CharField(label=_("Heading"), required=False, max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
    single_open = forms.BooleanField(
        label=_("Only open one answer at a time"),
        required=False,
        initial=True,
    )


@components.register
class SpaceGameFAQItem(CMSFrontendComponent):
    class Meta:
        name = _("Space Game FAQ Item")
        module = "Space Game"
        render_template = "theme/components/faq_item.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameFAQPlugin"]

    class PluginMixin:
        def render(self, context, instance, placeholder):
            group = context.get("faq_group")
            if group is None or group.pk != instance.parent_id:
                group = instance.parent.get_plugin_instance()[0]
            context = super().render(context, instance, placeholder)
            context["faq_single_open"] = bool(group.config.get("single_open", True))
            context["faq_schema_entry"] = faq_schema_entry(
                instance.config.get("question"),
                instance.config.get("answer"),
            )
            return context

    question = forms.CharField(label=_("Question"), max_length=400)
    answer = forms.CharField(label=_("Answer"), widget=forms.Textarea)
    initially_open = forms.BooleanField(label=_("Open initially"), required=False)

    def get_short_description(self):
        return self.config.get("question", "")


@components.register
class SpaceGameRequirements(CMSFrontendComponent):
    class Meta:
        name = _("Space Game System Requirements")
        module = "Space Game"
        render_template = "theme/components/requirements.html"
        child_classes = ["SpaceGameRequirementPlugin"]
        default_config = {
            "title": "System requirements",
            "component_label": "Component",
            "minimum_label": "Minimum",
            "recommended_label": "Recommended",
        }

    title = forms.CharField(label=_("Heading"), max_length=250)
    component_label = forms.CharField(label=_("Component column"), max_length=100)
    minimum_label = forms.CharField(label=_("Minimum column"), max_length=100)
    recommended_label = forms.CharField(label=_("Recommended column"), max_length=100)
    note = forms.CharField(label=_("Note"), required=False, widget=forms.Textarea)


@components.register
class SpaceGameRequirement(CMSFrontendComponent):
    class Meta:
        name = _("Space Game System Requirement")
        module = "Space Game"
        render_template = "theme/components/requirement.html"
        allow_children = False
        require_parent = True
        parent_classes = ["SpaceGameRequirementsPlugin"]

    title = forms.CharField(label=_("Component"), max_length=200)
    minimum = forms.CharField(label=_("Minimum"), widget=forms.Textarea)
    recommended = forms.CharField(label=_("Recommended"), widget=forms.Textarea)


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
        allow_children = True
        child_classes = ["TextLinkPlugin"]
        require_parent = True
        parent_classes = ["SpaceGameLauncherPlugin"]

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            context["launcher"] = instance.parent.get_plugin_instance()[0]
            attached = launcher_file(instance.config)
            context["launcher_file"] = attached
            context["launcher_filename"] = (
                attached.original_filename or attached.file.name.rsplit("/", 1)[-1]
                if attached
                else instance.config.get("filename", "")
            )
            context["launcher_available"] = (
                bool(attached)
                if instance.config.get("launcher_file")
                else bool(launcher_url(instance.config))
            )
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
    launcher_file = AdminFileFormField(
        label=_("Launcher file"),
        rel=ManyToOneRel(FilerFileField, File, "id"),
        queryset=File.objects.all(),
        to_field_name="id",
        required=False,
        help_text=_(
            "Select or upload a public launcher file. Takes priority over the URL.",
        ),
    )
    download_url = forms.URLField(
        label=_("Launcher download URL"),
        required=False,
        help_text=_(
            "HTTPS URL. Leave empty to use the environment URL for this platform.",
        ),
    )
    filename = forms.CharField(
        label=_("File name"),
        required=False,
        max_length=250,
        help_text=_("For external URLs. Uploaded files use their original filename."),
    )
    size = forms.CharField(
        label=_("File size"),
        required=False,
        max_length=100,
        help_text=_("For external URLs. Uploaded file sizes are shown automatically."),
    )
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

    def clean_launcher_file(self):
        attached = self.cleaned_data["launcher_file"]
        if attached and not attached.is_public:
            raise forms.ValidationError(
                _("Choose a public file for launcher downloads."),
            )
        return attached


@components.register
class SpaceGameDownloadInfo(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Download Info")
        module = "Space Game"
        render_template = "theme/components/download_info.html"
        allow_children = True
        child_classes = ["TextLinkPlugin"]

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
        allow_children = True
        child_classes = ["TextLinkPlugin"]
        default_config = {
            "eyebrow": "Exploration · Trade · Mining",
            "title": "Chart the unknown.",
            "description": (
                "A calm, technical space game. Fly into uncharted systems, mine "
                "resources and trade them between stations – at your own pace."  # noqa: RUF001
            ),
            "image_alt": "A space station against a glowing nebula",
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
    layout = forms.ChoiceField(
        label=_("Hero layout"),
        required=False,
        choices=[("", _("Full height")), ("compact", _("Compact"))],
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
        allow_children = True
        child_classes = ["TextLinkPlugin"]
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


class ContributorBioWidget(AdminTextareaWidget):
    template_name = "theme/widgets/contributor_bio.html"

    class Media:
        js = ("js/contributor-bio.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget = context["widget"]
        counter_id = f"{widget['attrs'].get('id', name)}-count"
        described_by = widget["attrs"].get("aria-describedby", "")
        widget["attrs"]["aria-describedby"] = f"{described_by} {counter_id}".strip()
        widget["attrs"]["data-contributor-counter"] = counter_id
        widget["counter_id"] = counter_id
        return context


CONTRIBUTOR_ROLES = {
    "moderation": {"de": "Moderation", "en": "Moderation"},
    "web": {"de": "Webentwicklung", "en": "Web Development"},
    "game": {"de": "Spielentwicklung", "en": "Game Development"},
    "design": {"de": "Game Design", "en": "Game Design"},
    "community": {"de": "Community", "en": "Community"},
    "accessibility": {"de": "Barrierefreiheit", "en": "Accessibility"},
}


def _shared_contributor_cards(request, instance, source_language):
    slot = instance.placeholder
    page_content = slot.source
    if not isinstance(page_content, PageContent):
        return []
    source = PageContent.objects.filter(
        page_id=page_content.page_id,
        language=source_language,
    ).first()
    if source is None:
        return []
    source_slot = source.placeholders.filter(slot=slot.slot).first()
    for group in get_plugins(
        request,
        source_slot,
        source.template,
        lang=source_language,
    ):
        if group.plugin_type == instance.plugin_type:
            return group.child_plugin_instances or []
    return []


@components.register
class SpaceGameContributors(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Contributors")
        module = "Space Game"
        render_template = "theme/components/contributors.html"
        allow_children = True
        child_classes = ["SpaceGameContributorPlugin"]

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            source_language = instance.config.get("source_language")
            shared = bool(source_language and source_language != instance.language)
            context["shared_contributors"] = shared
            context["contributor_cards"] = (
                _shared_contributor_cards(context["request"], instance, source_language)
                if shared
                else instance.child_plugin_instances
            )
            return context

    title = forms.CharField(label=_("Heading"), max_length=250)
    empty_label = forms.CharField(
        label=_("Empty directory message"),
        required=False,
        max_length=250,
    )
    source_language = forms.ChoiceField(
        label=_("Profile source"),
        required=False,
        choices=[
            ("", _("Cards in this plugin")),
            ("de", _("German page")),
            ("en", _("English page")),
        ],
        help_text=_(
            "Reuse published cards from the other language of this page. "
            "Edit the cards on the source page.",
        ),
    )


@components.register
class SpaceGameContributor(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Contributor Card")
        module = "Space Game"
        render_template = "theme/components/contributor.html"
        require_parent = True
        parent_classes = ["SpaceGameContributorsPlugin"]
        allow_children = True
        child_classes = ["SpaceGameContributorRolePlugin"]

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            lang = language()
            name = instance.config.get("name", "")
            context["contributor_bio"] = instance.config.get(f"bio_{lang}", "")
            context["contributor_initials"] = "".join(
                word[0] for word in name.split()[:2]
            )
            links = (
                ("Instagram", "instagram_url"),
                ("LinkedIn", "linkedin_url"),
                ("GitHub", "github_url"),
                ("Webseite" if lang == "de" else "Website", "website_url"),
            )
            context["contributor_links"] = [
                (label, instance.config[field])
                for label, field in links
                if instance.config.get(field)
            ]
            return context

    name = forms.CharField(label=_("Name"), max_length=150)
    image = ImageFormField(label=_("Portrait"), required=False)
    bio_de = forms.CharField(
        label="Kurzprofil (Deutsch)",
        required=False,
        max_length=500,
        widget=ContributorBioWidget,
    )
    bio_en = forms.CharField(
        label="Bio (English)",
        required=False,
        max_length=500,
        widget=ContributorBioWidget,
    )
    instagram_url = forms.URLField(
        label="Instagram",
        required=False,
        assume_scheme="https",
    )
    linkedin_url = forms.URLField(
        label="LinkedIn",
        required=False,
        assume_scheme="https",
    )
    github_url = forms.URLField(label="GitHub", required=False, assume_scheme="https")
    website_url = forms.URLField(
        label=_("Website"),
        required=False,
        assume_scheme="https",
    )

    def get_short_description(self):
        return self.config.get("name", "")


@components.register
class SpaceGameContributorRole(CMSFrontendComponent):
    class Meta:
        name = _("Space Game Contributor Role")
        module = "Space Game"
        render_template = "theme/components/contributor_role.html"
        require_parent = True
        parent_classes = ["SpaceGameContributorPlugin"]
        allow_children = False

    class PluginMixin:
        def render(self, context, instance, placeholder):
            context = super().render(context, instance, placeholder)
            lang = language()
            preset = CONTRIBUTOR_ROLES.get(instance.config.get("preset"), {})
            context["contributor_role"] = instance.config.get(
                f"label_{lang}",
            ) or preset.get(lang, "")
            return context

    preset = forms.ChoiceField(
        label=_("Role preset"),
        required=False,
        choices=[
            ("", _("Custom role")),
            *[(key, role["en"]) for key, role in CONTRIBUTOR_ROLES.items()],
        ],
    )
    label_de = forms.CharField(label="Rolle (Deutsch)", required=False, max_length=60)
    label_en = forms.CharField(label="Role (English)", required=False, max_length=60)

    def clean(self):
        data = super().clean()
        if not data.get("preset"):
            for field in ("label_de", "label_en"):
                if not data.get(field) and field not in self.errors:
                    self.add_error(field, _("Enter a label or choose a role preset."))
        return data

    def get_short_description(self):
        return (
            self.config.get("label_en")
            or self.config.get("label_de")
            or CONTRIBUTOR_ROLES.get(self.config.get("preset"), {}).get("en", "")
        )


@components.register
class SpaceGameCTA(CMSFrontendComponent):
    class Meta:
        name = _("Space Game CTA")
        module = "Space Game"
        render_template = "theme/components/cta.html"
        allow_children = True
        child_classes = ["TextLinkPlugin"]
        default_config = {
            "eyebrow": "",
            "title": "Ready for your first launch?",
            "description": (
                "Download the launcher for Windows or Linux. No account required."
            ),
        }

    eyebrow = forms.CharField(label=_("Eyebrow"), required=False, max_length=200)
    title = forms.CharField(label=_("Heading"), max_length=250)
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea,
    )
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
