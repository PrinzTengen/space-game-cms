"""Install the versioned Contributor page and editable frontend plugins."""

from cms.api import add_plugin
from cms.api import create_page
from cms.api import create_page_content
from cms.models import Page
from cms.models import PageContent
from cms.models import PageUrl
from cms.utils.placeholder import rescan_placeholders_for_obj
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_versioning.models import Version

from space_game.theme.install import unchanged_frontend_draft

TEMPLATE = "cms/contributors.html"
SLUG = "contributor"
HERO_COPY = {
    "de": (
        "Die Menschen hinter Space Game",
        (
            "Von der Spielmechanik bis zum Discord: "
            "Diese Menschen bringen das Projekt gemeinsam voran."
        ),
        "Die Profile folgen.",
    ),
    "en": (
        "Meet the people behind Space Game",
        (
            "From game mechanics to Discord, these are the people "
            "moving the project forward."
        ),
        "Profiles are coming soon.",
    ),
}


def install_language(page, language, user, created_content=None):
    published = PageContent.objects.filter(page=page, language=language).first()
    if published and published.template == TEMPLATE:
        plugins = set(
            published.placeholders.values_list("cmsplugin__plugin_type", flat=True),
        )
        if {"SpaceGameHeroPlugin", "SpaceGameContributorsPlugin"} <= plugins:
            return False

    draft = PageContent.admin_manager.filter(
        page=page,
        language=language,
        versions__state="draft",
    ).first()
    if (
        draft
        and draft != created_content
        and (published is None or not unchanged_frontend_draft(published, draft))
    ):
        msg = f"Contributor ({language}) has an unpublished edited draft."
        raise CommandError(msg)

    if draft:
        version = Version.objects.get_for_content(draft)
    elif published:
        version = Version.objects.get_for_content(published).copy(user)
    else:
        content = create_page_content(
            language,
            "Contributor",
            page,
            slug=SLUG,
            template=TEMPLATE,
            created_by=user,
            in_navigation=True,
        )
        version = Version.objects.get_for_content(content)

    content = version.content
    if content.template != TEMPLATE:
        legacy_plugins = content.placeholders.exclude(
            slot__in=("content", "contributor_hero", "contributors"),
        ).filter(cmsplugin__isnull=False)
        if legacy_plugins.exists():
            msg = f"Contributor ({language}) has plugins outside the new template."
            raise CommandError(msg)
        content.template = TEMPLATE
        content.save(update_fields=["template"])

    slots = rescan_placeholders_for_obj(content)
    title, description, empty_label = HERO_COPY[language]
    hero = slots["contributor_hero"]
    if not hero.get_plugins().filter(plugin_type="SpaceGameHeroPlugin").exists():
        add_plugin(
            hero,
            "SpaceGameHeroPlugin",
            language,
            config={"title": title, "description": description, "layout": "compact"},
        )
    directory = slots["contributors"]
    if (
        not directory.get_plugins()
        .filter(plugin_type="SpaceGameContributorsPlugin")
        .exists()
    ):
        add_plugin(
            directory,
            "SpaceGameContributorsPlugin",
            language,
            config={
                "title": "Contributors",
                "empty_label": empty_label,
                "source_language": "de" if language == "en" else "",
            },
        )
    version.publish(user)
    return True


class Command(BaseCommand):
    help = "Install the editable German and English Contributor page."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        user = (
            get_user_model()
            .objects.filter(
                username=options["username"],
                is_active=True,
                is_superuser=True,
            )
            .first()
        )
        if user is None:
            msg = "Pass an existing active superuser with --username."
            raise CommandError(msg)

        pages = Page.objects.select_for_update().filter(site_id=settings.SITE_ID)
        page = pages.filter(reverse_id=SLUG).first()
        if page is None:
            page_ids = PageUrl.objects.filter(path=SLUG).values("page_id")
            page = pages.filter(pk__in=page_ids).first()
        created_content = None
        if page is None:
            page = create_page(
                "Contributor",
                TEMPLATE,
                "de",
                slug=SLUG,
                reverse_id=SLUG,
                site=Site.objects.get(pk=settings.SITE_ID),
                created_by=user,
                in_navigation=True,
            )
            created_content = PageContent.admin_manager.get(page=page, language="de")
        changed = sum(
            install_language(page, language, user, created_content)
            for language in ("de", "en")
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Installed Contributor plugins in {changed} language(s).",
            ),
        )
