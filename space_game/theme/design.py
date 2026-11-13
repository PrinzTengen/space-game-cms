"""Content from the supplied F2 Orbit website, shared by native Django templates."""

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import get_language
from djangocms_stories.models import PostContent


@lru_cache(maxsize=1)
def catalog():
    return json.loads(
        Path(__file__).with_name("design_content.json").read_text("utf-8"),
    )


def language():
    return "de" if (get_language() or "en").startswith("de") else "en"


def published_posts(lang=None):
    return (
        PostContent.objects.filter(language=lang or language())
        .filter(
            Q(post__date_published__lte=now()) | Q(post__date_published__isnull=True),
        )
        .filter(
            Q(post__date_published_end__gt=now())
            | Q(post__date_published_end__isnull=True),
        )
        .filter(Q(post__sites__isnull=True) | Q(post__sites=settings.SITE_ID))
        .select_related("post", "post__app_config", "post__main_image")
        .prefetch_related("post__tags")
        .order_by("-post__date_published", "-post_id")
        .distinct()
    )
