"""Published, editable Stories in the supplied marketing layouts."""

from math import ceil

from django import template
from django.utils.html import strip_tags

from space_game.theme.design import published_posts

register = template.Library()


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
def reading_minutes(content):
    return max(1, ceil(len(strip_tags(content.post_text).split()) / 200))


@register.simple_tag
def next_post(content):
    posts = list(published_posts(content.language))
    for index, item in enumerate(posts):
        if item.pk == content.pk and len(posts) > 1:
            return posts[(index + 1) % len(posts)]
    return None
