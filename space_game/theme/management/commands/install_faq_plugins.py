"""Convert the support page into native, versioned frontend components."""

from cms.models import PageContent
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_versioning.models import Version

from space_game.theme.faq import FAQ_PLUGIN_TYPES
from space_game.theme.faq import add_default_faq_plugins
from space_game.theme.install import unchanged_frontend_draft


class Command(BaseCommand):
    help = "Install editable FAQ, system requirements and support header plugins."

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
        changed = 0
        for content in PageContent.objects.filter(
            page__reverse_id="faq",
            page__site_id=settings.SITE_ID,
        ):
            if content.placeholders.filter(
                cmsplugin__plugin_type__in=FAQ_PLUGIN_TYPES,
            ).exists():
                continue
            draft = PageContent.admin_manager.filter(
                page=content.page,
                language=content.language,
                versions__state="draft",
            ).first()
            if draft and not unchanged_frontend_draft(content, draft):
                msg = f"FAQ ({content.language}) has an unpublished edited draft."
                raise CommandError(msg)
            version = (
                Version.objects.get_for_content(draft)
                if draft
                else Version.objects.get_for_content(content).copy(user)
            )
            editable = version.content
            editable.template = "cms/faq.html"
            editable.save(update_fields=["template"])
            add_default_faq_plugins(editable)
            version.publish(user)
            changed += 1
        self.stdout.write(
            self.style.SUCCESS(f"Installed FAQ plugins on {changed} page(s)."),
        )
