"""Convert the former template hero into a versioned frontend component."""

from cms.models import PageContent
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_versioning.constants import DRAFT
from djangocms_versioning.constants import PUBLISHED
from djangocms_versioning.models import Version

from space_game.theme.hero import add_default_hero
from space_game.theme.install import unchanged_frontend_draft


class Command(BaseCommand):
    help = "Install the frontend Hero on existing landing homepages."
    slot = "hero"
    label = "Hero"
    installer = staticmethod(add_default_hero)

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

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
            msg = "Pass an existing active superuser with --username."
            raise CommandError(msg)

        contents = PageContent.admin_manager.filter(
            page__is_home=True,
            page__site_id=settings.SITE_ID,
            template="cms/home.html",
        )
        changed = 0
        for content in contents:
            version = Version.objects.get_for_content(content)
            if version.state != PUBLISHED:
                continue
            placeholder = content.get_placeholders().get(slot=self.slot)
            if placeholder.get_plugins(language=content.language).exists():
                continue
            draft = contents.filter(
                page=content.page,
                language=content.language,
                versions__state=DRAFT,
            ).first()
            if draft:
                # Opening the editor creates a draft even before anything changes.
                if not unchanged_frontend_draft(content, draft):
                    msg = (
                        f"Homepage ({content.language}) has an unpublished draft. "
                        f"Add the {self.label} in its {self.slot} placeholder "
                        "and publish it."
                    )
                    raise CommandError(msg)
                new_version = Version.objects.get_for_content(draft)
            else:
                new_version = version.copy(user)
            self.installer(new_version.content)
            new_version.publish(user)
            changed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Installed {self.label} on {changed} homepage(s)."),
        )
