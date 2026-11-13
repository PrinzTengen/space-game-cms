"""Install editable public downloads without overwriting editorial drafts."""

from cms.models import PageContent
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_versioning.models import Version

from space_game.theme.design import catalog
from space_game.theme.downloads import DOWNLOAD_PLUGIN_TYPES
from space_game.theme.downloads import add_default_download_plugins
from space_game.theme.install import unchanged_frontend_draft

LEGACY_COPY = {
    "en": {
        "note": "Pre-Alpha for Windows & Linux · Sign in with Discord",
        "description": (
            "Sign in with Discord and download the launcher for Windows or Linux."
        ),
    },
    "de": {
        "note": "Pre-Alpha für Windows & Linux · Anmeldung über Discord",
        "description": (
            "Melde dich mit Discord an und lade den Launcher "
            "für Windows oder Linux herunter."
        ),
    },
}


class Command(BaseCommand):
    help = "Install download plugins and remove stock copy requiring Discord sign-in."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @staticmethod
    def draft_for(content):
        return PageContent.admin_manager.filter(
            page=content.page,
            language=content.language,
            versions__state="draft",
        ).first()

    @staticmethod
    def editable_version(content, draft, user):
        return (
            Version.objects.get_for_content(draft)
            if draft
            else Version.objects.get_for_content(content).copy(user)
        )

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
        changed = 0
        for content in PageContent.objects.filter(
            page__reverse_id="download",
            page__site_id=settings.SITE_ID,
        ):
            if content.placeholders.filter(
                cmsplugin__plugin_type__in=DOWNLOAD_PLUGIN_TYPES,
            ).exists():
                continue
            draft = self.draft_for(content)
            if draft and not unchanged_frontend_draft(content, draft):
                msg = f"Download ({content.language}) has an unpublished edited draft."
                raise CommandError(msg)
            version = self.editable_version(content, draft, user)
            add_default_download_plugins(version.content)
            version.publish(user)
            changed += 1
        self.update_home_copy(user)
        self.stdout.write(
            self.style.SUCCESS(
                f"Installed public download plugins on {changed} page(s).",
            ),
        )

    def update_home_copy(self, user):
        for content in PageContent.objects.filter(
            page__is_home=True,
            page__site_id=settings.SITE_ID,
        ):
            if not self.stock_copy_changes(content):
                continue
            draft = self.draft_for(content)
            if draft and not unchanged_frontend_draft(content, draft):
                self.stderr.write(
                    f"Preserved edited homepage draft ({content.language}); "
                    "update sign-in copy manually.",
                )
                continue
            version = self.editable_version(content, draft, user)
            for instance, field, replacement in self.stock_copy_changes(
                version.content,
            ):
                instance.config[field] = replacement
                instance.save()
            version.publish(user)

    @staticmethod
    def stock_copy_changes(content):
        legacy = LEGACY_COPY.get(content.language, {})
        strings = catalog()["strings"][content.language]["home"]
        changes = []
        for placeholder in content.placeholders.all():
            for plugin in placeholder.get_plugins().filter(
                plugin_type__in=["SpaceGameHeroPlugin", "SpaceGameCTAPlugin"],
            ):
                instance = plugin.get_plugin_instance()[0]
                field = (
                    "note"
                    if plugin.plugin_type == "SpaceGameHeroPlugin"
                    else "description"
                )
                if instance.config.get(field) == legacy.get(field):
                    changes.append(
                        (
                            instance,
                            field,
                            strings["note" if field == "note" else "ctaText"],
                        ),
                    )
        return changes
