"""Create the initial CMS page tree without replacing existing editorial content."""

from cms.api import add_plugin
from cms.api import create_page
from cms.models import Page
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.cms_appconfig import config_defaults
from djangocms_versioning.models import Version

from space_game.theme.cards import add_default_cards
from space_game.theme.cta import add_default_cta
from space_game.theme.hero import add_default_hero


class Command(BaseCommand):
    help = "Create and publish Home, About and Stories pages (existing pages are kept)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Existing superuser owning the initial versions.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        user = (
            get_user_model()
            .objects.filter(
                username=options["username"],
                is_superuser=True,
                is_active=True,
            )
            .first()
        )
        if user is None:
            msg = (
                "Create an active superuser first, then pass its username "
                "with --username."
            )
            raise CommandError(msg)

        site = Site.objects.get(pk=settings.SITE_ID)
        language = settings.LANGUAGE_CODE
        home = Page.objects.filter(site=site, is_home=True).first()
        if home is None:
            home = self.create_page(
                user,
                site,
                language,
                "Home",
                "home",
                "",
            )
            home.set_as_homepage(user=user)

        if not Page.objects.filter(site=site, reverse_id="about").exists():
            self.create_page(
                user,
                site,
                language,
                "About",
                "about",
                "<h1>About Space Game</h1>",
            )

        if not Page.objects.filter(site=site, reverse_id="stories").exists():
            config, _ = StoriesConfig.objects.get_or_create(
                namespace="stories",
                defaults={"type": "StoriesApp", **config_defaults},
            )
            if not config.has_translation(language):
                config.set_current_language(language)
                config.app_title = "Stories"
                config.object_name = "Article"
                config.save()
            self.create_page(
                user,
                site,
                language,
                "Stories",
                "stories",
                "",
                apphook="StoriesApp",
                apphook_namespace=config.namespace,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "CMS pages are ready. Configure Cookie Love in the admin.",
            ),
        )

    @staticmethod
    def create_page(user, site, language, title, slug, body, **kwargs):  # noqa: PLR0913, PLR0917
        page = create_page(
            title,
            "cms/home.html" if slug == "home" else "cms/default.html",
            language,
            slug=slug,
            reverse_id=slug,
            site=site,
            created_by=user,
            in_navigation=True,
            **kwargs,
        )
        content = page.pagecontent_set(manager="admin_manager").get(language=language)
        if slug == "home":
            add_default_hero(content)
            add_default_cards(content)
            add_default_cta(content)
        if body:
            add_plugin(
                content.get_placeholders().get(slot="content"),
                "TextPlugin",
                language,
                body=body,
            )
        Version.objects.get_for_content(content).publish(user)
        return page
