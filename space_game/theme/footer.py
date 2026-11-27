"""Seed and publish the static footer alias rendered by base.html."""

from cms.api import add_plugin
from cms.models import Page
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.core.management.base import CommandError
from djangocms_alias.constants import DEFAULT_STATIC_ALIAS_CATEGORY_NAME
from djangocms_alias.models import Alias
from djangocms_alias.models import AliasContent
from djangocms_alias.models import Category
from djangocms_versioning.constants import DRAFT
from djangocms_versioning.constants import PUBLISHED
from djangocms_versioning.models import Version

from space_game.theme.design import catalog

FOOTER_CODE = "footer"
FOOTER_SLOTS = ("pages", "community", "legal")
DISCORD_URL = "https://discord.gg/TeGQrqprRM"


def footer_alias():
    """Return the site-independent alias behind {% static_alias "footer" %}."""
    alias = Alias.objects.filter(static_code=FOOTER_CODE, site__isnull=True).first()
    if alias:
        return alias
    # Parler's get_or_create does not handle translated fields.
    category = Category.objects.filter(
        translations__name=DEFAULT_STATIC_ALIAS_CATEGORY_NAME,
    ).first() or Category.objects.create(name=DEFAULT_STATIC_ALIAS_CATEGORY_NAME)
    return Alias.objects.create(
        category=category,
        static_code=FOOTER_CODE,
        creation_method=Alias.CREATION_BY_TEMPLATE,
    )


def _page_links(strings):
    site_pages = Page.objects.filter(site_id=settings.SITE_ID)
    for key, lookup in [
        ("home", {"is_home": True}),
        ("blog", {"reverse_id": "stories"}),
        ("download", {"reverse_id": "download"}),
        ("faq", {"reverse_id": "faq"}),
    ]:
        page = site_pages.filter(**lookup).first()
        if page:
            yield strings["nav"][key], {"internal_link": f"cms.page:{page.pk}"}


def _community_links():
    yield "Discord", {"external_link": DISCORD_URL}
    if settings.SG_TWITCH_URL:
        yield "Twitch", {"external_link": settings.SG_TWITCH_URL}


def _add_link(placeholder, language, slot, label, link):
    add_plugin(
        placeholder,
        "TextLinkPlugin",
        language,
        target=slot,
        config={
            "name": label,
            "link": link,
            "template": "default",
            "link_type": "link",
            "link_context": "",
            "link_size": "",
            "target": "",
        },
    )


def add_default_footer(content, strings):
    """Add the footer component, its slots and the default links."""
    placeholder = content.placeholder
    language = content.language
    plugin = plugin_pool.get_plugin("SpaceGameFooterPlugin")
    config = plugin.model().initialize_from_form(plugin.form).config
    foot = strings["foot"]
    config.update(
        tagline=foot["line"],
        pages_label=foot["pages"],
        community_label=foot["community"],
        legal_label=foot["legal"],
        rights=foot["rights"],
        show_cookie_settings=True,
    )
    footer = add_plugin(placeholder, "SpaceGameFooterPlugin", language, config=config)
    links = {
        "pages": list(_page_links(strings)),
        "community": list(_community_links()),
        "legal": [],
    }
    # The API bypasses the editor, which would otherwise create the slots.
    # Build depth-first: CMS positions must list every slot directly before its
    # links, and add_plugin derives the position from the in-memory target.
    for name in FOOTER_SLOTS:
        footer.refresh_from_db()
        slot = add_plugin(
            placeholder,
            f"SpaceGameFooter{name.capitalize()}Plugin",
            language,
            target=footer,
        )
        for label, link in links[name]:
            slot.refresh_from_db()
            _add_link(placeholder, language, slot, label, link)
    return footer


def install_footer(user):
    """Publish the default footer per language; never overwrite editorial work."""
    alias = footer_alias()
    strings = catalog()["strings"]
    changed = 0
    for language in ("en", "de"):
        contents = AliasContent.admin_manager.filter(alias=alias, language=language)
        published = contents.filter(versions__state=PUBLISHED).first()
        if published and published.placeholder.get_plugins().exists():
            continue
        draft = contents.filter(versions__state=DRAFT).first()
        if draft:
            if draft.placeholder.get_plugins().exists():
                msg = (
                    f"The footer ({language}) has an unpublished draft. "
                    "Publish or discard it, then run this command again."
                )
                raise CommandError(msg)
            version = Version.objects.get_for_content(draft)
        elif published:
            version = Version.objects.get_for_content(published).copy(user)
        else:
            content = AliasContent.objects.with_user(user).create(
                alias=alias,
                name=FOOTER_CODE,
                language=language,
            )
            version = Version.objects.get_for_content(content)
        add_default_footer(version.content, strings[language])
        version.publish(user)
        changed += 1
    return changed
