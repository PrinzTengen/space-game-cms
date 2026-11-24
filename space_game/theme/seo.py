"""Crawler entry points: sitemap.xml, robots.txt and llms.txt.

URLs carry no language prefix (the language comes from a cookie), so English and
German pages often share one path. Every list here is deduplicated by URL.
"""

from cms.models import PageContent
from cms.sitemaps.cms_sitemap import CMSSitemap
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.urls import NoReverseMatch
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from space_game.theme.design import published_posts

# Public paths that only serve forms, redirects, APIs or large binaries.
# ADMIN_URL is deliberately not listed: production keeps it secret, and naming
# it here would publish it.
ROBOTS_DISALLOW = [
    "/api/",
    "/oauth/",
    "/users/",
    "/i18n/",
    "/cookie-love/",
    "/launcher/",
]


def _languages():
    return [code for code, _name in settings.LANGUAGES]


class PageSitemap(CMSSitemap):
    """Published, public CMS pages, one entry per distinct URL."""

    changefreq = "weekly"

    def items(self):
        seen = set()
        unique = []
        for page_url in super().items():
            location = self.location(page_url)
            if location not in seen:
                seen.add(location)
                unique.append(page_url)
        return unique

    def priority(self, page_url):
        return 1.0 if page_url.page.is_home else 0.7


def _story_entries():
    """Yield (location, PostContent) for published stories, unique by URL."""
    seen = set()
    for lang in _languages():
        for content in published_posts(lang):
            try:
                location = content.get_absolute_url(language=lang)
            except NoReverseMatch:
                continue
            if location and location not in seen:
                seen.add(location)
                yield location, content


class StorySitemap(Sitemap):
    """Published stories; scheduled and expired posts stay out."""

    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return list(_story_entries())

    def location(self, item):
        return item[0]

    def lastmod(self, item):
        return item[1].post.date_modified


sitemaps = {"pages": PageSitemap, "stories": StorySitemap}


def _absolute(request, path):
    """Same origin the sitemap framework uses, so all three files agree."""
    return f"{request.scheme}://{get_current_site(request).domain}{path}"


def _text(response_body):
    return HttpResponse(response_body, content_type="text/plain; charset=utf-8")


@require_GET
@cache_control(max_age=3600, public=True)
def robots_txt(request):
    lines = ["User-agent: *"]
    lines += [f"Disallow: {path}" for path in ROBOTS_DISALLOW]
    lines += [
        "Allow: /",
        "",
        f"Sitemap: {_absolute(request, '/sitemap.xml')}",
        "",
    ]
    return _text("\n".join(lines))


def _summary(value, words=40):
    return Truncator(strip_tags(value or "").strip()).words(words, truncate="…")


def _link(title, url, description=""):
    line = f"- [{title}]({url})"
    return f"{line}: {description}" if description else line


def _page_lines(request, language):
    lines = []
    sitemap = PageSitemap()
    for page_url in sitemap.items():
        if page_url.language != language:
            continue
        content = PageContent.objects.filter(
            page=page_url.page,
            language=language,
        ).first()
        if content is None:
            continue
        lines.append(
            _link(
                content.page_title or content.title,
                _absolute(request, sitemap.location(page_url)),
                _summary(content.meta_description),
            ),
        )
    return lines


def _story_lines(request, language, limit=50):
    lines = []
    for location, content in _story_entries():
        if content.language != language:
            continue
        lines.append(
            _link(
                content.title,
                _absolute(request, location),
                _summary(
                    content.meta_description or content.abstract or content.subtitle,
                ),
            ),
        )
        if len(lines) >= limit:
            break
    return lines


@require_GET
@cache_control(max_age=3600, public=True)
def llms_txt(request):
    """Markdown overview for language models, following llmstxt.org."""
    language = settings.LANGUAGE_CODE
    home = PageContent.objects.filter(page__is_home=True, language=language).first()
    summary = _summary(home.meta_description if home else "", words=60) or (
        "Space Game is a video game. This site hosts the launcher download, "
        "system requirements, FAQ and development stories."
    )
    parts = [
        "# Space Game",
        "",
        f"> {summary}",
        "",
        (
            "The site is available in English and German. Both languages share "
            "the same URLs; the language is chosen by the visitor and stored in "
            "a cookie."
        ),
        "",
        "## Pages",
        "",
        *_page_lines(request, language),
    ]
    stories = _story_lines(request, language)
    if stories:
        parts += ["", "## Stories", "", *stories]
    parts += [
        "",
        "## Optional",
        "",
        _link(
            "Sitemap",
            _absolute(request, "/sitemap.xml"),
            "every public page and story, in all languages",
        ),
        "",
    ]
    return _text("\n".join(parts))
