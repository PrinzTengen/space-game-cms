"""Install the supplied F2 Orbit content while preserving CMS version history."""

from datetime import UTC
from datetime import datetime

from cms.api import create_page
from cms.api import create_page_content
from cms.models import Page
from cms.models import PageContent
from cms.utils.plugins import copy_plugins_to_placeholder
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils.html import format_html
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.theme.buttons import BUTTON_FIELDS
from space_game.theme.buttons import add_plugin
from space_game.theme.buttons import convert_buttons
from space_game.theme.design import catalog
from space_game.theme.install import unchanged_frontend_draft

DESIGN_VERSION = "f2-orbit-v1"


class Command(BaseCommand):
    help = "Apply the supplied F2 Orbit website and DE/EN content."

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
        call_command("bootstrap_cms", username=user.username)
        data = catalog()
        home = Page.objects.get(site_id=settings.SITE_ID, is_home=True)
        stories = Page.objects.get(site_id=settings.SITE_ID, reverse_id="stories")
        for lang in ("en", "de"):
            self.install_home(home, lang, user, data["strings"][lang])
            self.ensure_translation(
                stories,
                lang,
                user,
                data["strings"][lang]["blog"]["title"],
            )
        for slug, template, label in [
            ("download", "cms/download.html", "download"),
            ("faq", "cms/faq.html", "faq"),
        ]:
            page = Page.objects.filter(
                site_id=settings.SITE_ID,
                reverse_id=slug,
            ).first()
            if page is None:
                page = create_page(
                    data["strings"]["en"]["nav"][label],
                    template,
                    "en",
                    slug=slug,
                    reverse_id=slug,
                    site=Site.objects.get(pk=settings.SITE_ID),
                    created_by=user,
                )
                created = PageContent.admin_manager.get(page=page, language="en")
                Version.objects.get_for_content(created).publish(user)
            for lang in ("en", "de"):
                self.ensure_translation(
                    page,
                    lang,
                    user,
                    data["strings"][lang]["nav"][label],
                )
        self.install_posts(user, data)
        call_command("install_home_stories", username=user.username)
        call_command("install_logbook_header", username=user.username)
        call_command("install_download_plugins", username=user.username)
        call_command("install_faq_plugins", username=user.username)
        self.stdout.write(
            self.style.SUCCESS("F2 Orbit website installed in DE and EN."),
        )

    @staticmethod
    def ensure_translation(page, lang, user, title):
        content = PageContent.admin_manager.filter(page=page, language=lang).first()
        if content:
            return content
        original = PageContent.admin_manager.filter(page=page, language="en").first()
        content = create_page_content(
            lang,
            title,
            page,
            created_by=user,
            slug=page.get_slug("en"),
            template=original.template,
            in_navigation=True,
        )
        Version.objects.get_for_content(content).publish(user)
        return content

    def install_home(self, page, lang, user, strings):
        published = PageContent.objects.filter(page=page, language=lang).first()
        if published:
            hero = (
                published.get_placeholders()
                .get(slot="hero")
                .get_plugins()
                .filter(
                    plugin_type="SpaceGameHeroPlugin",
                )
                .first()
            )
            if (
                hero
                and hero.get_plugin_instance()[0].config.get("_design_system")
                == DESIGN_VERSION
            ):
                return
            draft = PageContent.admin_manager.filter(
                page=page,
                language=lang,
                versions__state="draft",
            ).first()
            if draft and not unchanged_frontend_draft(published, draft):
                msg = (
                    f"Homepage ({lang}) has an edited unpublished draft; "
                    "preserve and publish it first."
                )
                raise CommandError(msg)
            version = (
                Version.objects.get_for_content(draft)
                if draft
                else Version.objects.get_for_content(published).copy(user)
            )
            content = version.content
        else:
            content = create_page_content(
                lang,
                "Start" if lang == "de" else "Home",
                page,
                created_by=user,
                slug="",
                template="cms/home.html",
                in_navigation=True,
            )
            version = Version.objects.get_for_content(content)
            original = PageContent.objects.filter(page=page, language="en").first()
            if original:
                source = original.get_placeholders().get(slot="gallery")
                target = content.get_placeholders().get(slot="gallery")
                copy_plugins_to_placeholder(
                    source.get_plugins().order_by("position"),
                    target,
                    lang,
                )
        home = strings["home"]
        self.configure(
            content,
            "hero",
            "SpaceGameHeroPlugin",
            {
                "_design_system": DESIGN_VERSION,
                "eyebrow": home["kicker"],
                "title": home["h1"],
                "description": home["lead"],
                "note": home["note"],
                "image": "",
                "image_alt": "Space Game / F2 Orbit",
                "primary_label": home["cta"],
                "primary_link": {"external_link": "/download/"},
                "secondary_label": home["cta2"],
                "secondary_link": {"external_link": "/stories/?type=devlog"},
            },
        )
        group = self.configure(
            content,
            "discovery",
            "SpaceGameCardsPlugin",
            {
                "eyebrow": home["pillarsLabel"],
                "title": home["pillarsTitle"],
            },
        )
        cards = list(group.get_children().order_by("position"))
        for index, pillar in enumerate(strings["pillars"]):
            config = {
                "title": pillar["title"],
                "description": pillar["text"],
                "eyebrow": "",
                "default_image": "",
                "image": "",
            }
            if index < len(cards):
                instance = cards[index].get_plugin_instance()[0]
                instance.config.update(config)
                instance.save()
            else:
                add_plugin(
                    group.placeholder,
                    "SpaceGameCardPlugin",
                    lang,
                    target=group,
                    config=config,
                )
        self.configure(
            content,
            "community",
            "SpaceGameCTAPlugin",
            {
                "eyebrow": "",
                "title": home["ctaTitle"],
                "description": home["ctaText"],
                "button_label": home["ctaBtn"],
                "button_link": {"external_link": "/download/"},
            },
        )
        version.publish(user)

    @staticmethod
    def configure(content, slot, plugin_type, config):
        placeholder = content.get_placeholders().get(slot=slot)
        plugin = placeholder.get_plugins().filter(plugin_type=plugin_type).first()
        if plugin:
            instance = plugin.get_plugin_instance()[0]
            instance.config.update(config)
            instance.save()
            # Update the seeded links while retaining their native button options.
            if plugin_type in {"SpaceGameHeroPlugin", "SpaceGameCTAPlugin"}:
                buttons = instance.get_children().filter(
                    plugin_type="TextLinkPlugin",
                ).order_by("position")
                for child, (label_key, link_key, _) in zip(
                    buttons, BUTTON_FIELDS[plugin_type], strict=False,
                ):
                    button = child.get_plugin_instance()[0]
                    button.config.update(
                        name=instance.config.pop(label_key),
                        link=instance.config.pop(link_key),
                    )
                    button.save()
                instance.save(update_fields=["config"])
                convert_buttons(instance)
            return plugin
        return add_plugin(placeholder, plugin_type, content.language, config=config)

    @staticmethod
    def install_posts(user, data):
        app_config = StoriesConfig.objects.get(namespace="stories")
        for entry in data["posts"]:
            existing = PostContent.admin_manager.filter(slug=entry["id"]).first()
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
            post.tags.add(entry["type"])
            for lang in ("en", "de"):
                if PostContent.admin_manager.filter(post=post, language=lang).exists():
                    continue
                copy = entry[lang]
                body = []
                for kind, text in copy["body"]:
                    if kind == "h":
                        body.append(format_html("<h2>{}</h2>", text))
                    elif kind == "img":
                        body.append(
                            format_html(
                                '<figure><div class="sg-media">{}</div>'
                                "<figcaption>{}</figcaption></figure>",
                                data["strings"][lang]["art"]["slot"],
                                text,
                            ),
                        )
                    else:
                        body.append(format_html("<p>{}</p>", text))
                content = PostContent.objects.with_user(user).create(
                    post=post,
                    language=lang,
                    slug=entry["id"],
                    title=copy["title"],
                    abstract=copy["excerpt"],
                    post_text="".join(body),
                    subtitle=f"Devlog #{entry['num']}"
                    if entry["type"] == "devlog"
                    else "News",
                )
                Version.objects.get_for_content(content).publish(user)
