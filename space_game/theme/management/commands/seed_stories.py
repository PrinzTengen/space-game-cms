"""Create complete, bilingual Stories using the supplied game imagery."""

import hashlib
import json
from datetime import UTC
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils.html import format_html
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post
from djangocms_stories.models import PostCategory
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version
from filer.models import Image

from space_game.theme.install import unchanged_frontend_draft


def story_catalog():
    return json.loads(
        Path(__file__)
        .resolve()
        .parents[2]
        .joinpath("story_content.json")
        .read_text("utf-8"),
    )


def render_body(copy):
    parts = []
    for kind, text in copy["body"]:
        parts.append(format_html("<h2>{}</h2>" if kind == "h" else "<p>{}</p>", text))
    return "".join(parts)


class Command(BaseCommand):
    help = "Create or complete five Devlogs and five News articles in DE and EN."

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
        if not user:
            msg = "Pass an existing active superuser with --username."
            raise CommandError(msg)
        app_config = StoriesConfig.objects.filter(namespace="stories").first()
        if not app_config:
            msg = "Run bootstrap_cms first."
            raise CommandError(msg)
        entries = story_catalog()
        self.validate_drafts(entries, app_config)
        categories = self.categories(app_config)
        changed = 0
        for entry in entries:
            existing = PostContent.admin_manager.filter(
                post__app_config=app_config,
                slug=entry["id"],
            ).first()
            post = (
                existing.post
                if existing
                else Post.objects.create(
                    author=user,
                    app_config=app_config,
                    date_published=datetime.fromisoformat(entry["date"]).replace(
                        tzinfo=UTC,
                    ),
                )
            )
            if post.author_id is None:
                post.author = user
                post.save(update_fields=["author"])
            if not post.main_image_id:
                post.main_image = self.cover(entry, user)
                post.save(update_fields=["main_image"])
            post.tags.add(entry["type"])
            post.categories.add(categories[entry["type"]])
            changed += sum(
                self.seed_translation(post, entry, lang, user) for lang in ("en", "de")
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Stories ready: 5 Devlogs, 5 News, DE/EN; "
                f"{changed} translations published.",
            ),
        )

    @staticmethod
    def validate_drafts(entries, app_config):
        for entry in entries:
            for lang in ("en", "de"):
                published = PostContent.objects.filter(
                    post__app_config=app_config,
                    slug=entry["id"],
                    language=lang,
                ).first()
                seeded = PostContent.admin_manager.filter(
                    post__app_config=app_config,
                    slug=entry["id"],
                    language=lang,
                    post_text=render_body(entry[lang]),
                ).exists()
                if seeded:
                    continue
                if published:
                    draft = PostContent.admin_manager.filter(
                        post=published.post,
                        language=lang,
                        versions__state="draft",
                    ).first()
                    if draft and not unchanged_frontend_draft(published, draft):
                        msg = f"{entry['id']} ({lang}) has an unpublished edited draft."
                        raise CommandError(msg)
                elif PostContent.admin_manager.filter(
                    post__app_config=app_config,
                    slug=entry["id"],
                    language=lang,
                    versions__state="draft",
                ).exists():
                    msg = f"{entry['id']} ({lang}) already has an unpublished draft."
                    raise CommandError(msg)

    @staticmethod
    def seed_translation(post, entry, lang, user):
        copy = entry[lang]
        text = render_body(copy)
        # Version history identifies an earlier import without public seed tags.
        if PostContent.admin_manager.filter(
            post=post,
            language=lang,
            post_text=text,
        ).exists():
            return 0
        published = PostContent.objects.filter(post=post, language=lang).first()
        draft = PostContent.admin_manager.filter(
            post=post,
            language=lang,
            versions__state="draft",
        ).first()
        if draft and not published:
            msg = f"{entry['id']} ({lang}) already has an unpublished draft."
            raise CommandError(msg)
        if published:
            version = (
                Version.objects.get_for_content(draft)
                if draft
                else Version.objects.get_for_content(published).copy(user)
            )
            content = version.content
        else:
            content = PostContent.objects.with_user(user).create(
                post=post,
                language=lang,
                slug=entry["id"],
                title=copy["title"],
            )
            version = Version.objects.get_for_content(content)
        content.title = copy["title"]
        content.slug = entry["id"]
        content.subtitle = (
            f"Devlog #{entry['num']}" if entry["type"] == "devlog" else "News"
        )
        content.abstract = format_html("<p>{}</p>", copy["excerpt"])
        content.meta_description = copy["excerpt"]
        content.post_text = text
        content.save()
        version.publish(user)
        return 1

    @staticmethod
    def cover(entry, user):
        source = (
            Path(settings.BASE_DIR) / "space_game/static/images/theme" / entry["cover"]
        )
        digest = hashlib.sha1(source.read_bytes(), usedforsecurity=False).hexdigest()
        image = Image.objects.filter(sha1=digest).first()
        if image:
            return image
        with source.open("rb") as handle:
            return Image.objects.create(
                file=File(handle, name=source.name),
                owner=user,
                original_filename=source.name,
                name=entry["en"]["title"],
                default_alt_text=entry["alt"],
            )

    @staticmethod
    def categories(app_config):
        result = {}
        for kind, english, german in [
            ("devlog", "Devlogs", "Devlogs"),
            ("news", "News", "News"),
        ]:
            category = PostCategory.objects.filter(
                app_config=app_config,
                translations__language_code="en",
                translations__slug=kind,
            ).first()
            if category is None:
                category = PostCategory(app_config=app_config)
            for lang, label in [("en", english), ("de", german)]:
                category.set_current_language(lang)
                category.name = label
                category.slug = kind
                category.save()
            result[kind] = category
        return result
