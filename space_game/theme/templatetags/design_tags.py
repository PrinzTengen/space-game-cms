"""Published, editable Stories in the supplied marketing layouts."""

from html import unescape
from math import ceil

from cms.toolbar.utils import get_toolbar_from_request
from django import template
from django.utils.html import strip_tags

from space_game.theme.design import published_posts

register = template.Library()


@register.filter
def cms_navigation_pages(nodes):
    """Keep CMS pages when apphooks extend the menu with their own entries."""
    return [node for node in nodes if node.attr.get("is_page")]


@register.simple_tag(takes_context=True)
def render_contributor_child(context, plugin, *, shared=False):
    toolbar = get_toolbar_from_request(context["request"])
    return toolbar.get_content_renderer().render_plugin(
        instance=plugin,
        context=context,
        editable=toolbar.edit_mode_active and not shared,
    )


@register.simple_tag
def design_posts(limit=None, kind="all"):
    posts = published_posts()
    if kind in {"news", "devlog"}:
        posts = posts.filter(post__tags__slug=kind)
    return posts[:limit] if limit else posts


@register.filter
def post_kind(content):
    return "devlog" if "devlog" in {t.slug for t in content.post.tags.all()} else "news"


@register.filter
def post_filter_slugs(content):
    """Space-separated filter keys of a card: its kind plus all tag slugs."""
    slugs = [post_kind(content)]
    slugs += [t.slug for t in content.post.tags.all() if t.slug not in slugs]
    return " ".join(slugs)


@register.simple_tag
def post_filter_tags(posts):
    """Tags used by the listed posts, apart from the built-in news/devlog filters."""
    tags = {}
    for content in posts:
        for tag in content.post.tags.all():
            if tag.slug not in {"news", "devlog"}:
                tags.setdefault(tag.slug, tag.name)
    return sorted(tags.items(), key=lambda item: item[1].casefold())


@register.filter
def post_search_text(content):
    text = " ".join(
        [
            content.title,
            content.subtitle,
            content.abstract,
            content.post_text,
            " ".join(tag.name for tag in content.post.tags.all()),
        ],
    )
    return " ".join(unescape(strip_tags(text.replace(">", "> "))).split())


@register.filter
def reading_minutes(content):
    return max(1, ceil(len(strip_tags(content.post_text).split()) / 200))


@register.simple_tag
def next_post(content):
    posts = list(published_posts(content.language))
    for index, item in enumerate(posts):
        if item.pk == content.pk and len(posts) > 1:
            return posts[(index + 1) % len(posts)]
    return None
