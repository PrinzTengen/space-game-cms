"""Complete bilingual editorial content with reusable, real Filer cover images."""

from http import HTTPStatus

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils.html import strip_tags
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version
from filer.models import Image

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def editorial_site(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    call_command("seed_stories", username=user.username)
    return user


def test_five_complete_devlogs_and_five_news(editorial_site, client, monkeypatch):
    assert Post.objects.count() == 10  # noqa: PLR2004
    assert Post.objects.filter(tags__slug="devlog").count() == 5  # noqa: PLR2004
    assert Post.objects.filter(tags__slug="news").count() == 5  # noqa: PLR2004
    assert PostContent.objects.count() == 20  # noqa: PLR2004
    assert Image.objects.count() == 10  # noqa: PLR2004
    for content in PostContent.objects.select_related("post", "post__main_image"):
        assert len(strip_tags(content.post_text).split()) >= 240  # noqa: PLR2004
        assert content.post_text.count("<h2>") == 4  # noqa: PLR2004
        assert content.abstract
        assert content.meta_description
        assert content.post.author_id == editorial_site.pk
        assert content.post.main_image.file.storage.exists(
            content.post.main_image.file.name,
        )
        assert content.post.main_image.default_alt_text
        assert content.categories.count() == 1
        client.post(
            reverse("set_language"),
            {"language": content.language, "next": "/"},
        )
        detail = client.get(content.get_absolute_url())
        assert detail.status_code == HTTPStatus.OK
        assert detail.content.count(b"<h2>") == 4  # noqa: PLR2004
        assert content.post.main_image.url.encode() in detail.content
    client.post(reverse("set_language"), {"language": "en", "next": "/"})
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b'class="sg-window sg-post-card"') == 3  # noqa: PLR2004
    assert b"Drop image" not in response.content
    assert b"Stationen im richtigen Licht" not in response.content  # English homepage.
    assert b"Stations in the right light" in response.content
    monkeypatch.setattr("meta.models.get_request", lambda: None)
    # Uvicorn does not expose a thread-local request to Stories' metadata hooks.
    content = PostContent.objects.select_related("post__main_image").first()
    monkeypatch.setattr(
        content.post.main_image.file.storage,
        "url",
        lambda _name: "/media/cover.png",
    )
    assert content.get_image_full_url().startswith("https://")


def test_reseed_keeps_images_versions_and_later_editorial_changes(editorial_site):
    content = PostContent.objects.get(slug="devlog-9", language="en")
    draft = Version.objects.get_for_content(content).copy(editorial_site)
    draft.content.post_text = "<p>A later editorial revision.</p>"
    draft.content.save()
    draft.publish(editorial_site)
    versions = Version.objects.count()
    images = list(Image.objects.values_list("pk", flat=True))
    call_command("seed_stories", username=editorial_site.username)
    assert Version.objects.count() == versions
    assert list(Image.objects.values_list("pk", flat=True)) == images
    assert (
        PostContent.objects.get(slug="devlog-9", language="en").post_text
        == "<p>A later editorial revision.</p>"
    )


def test_seed_preserves_unpublished_post_edits(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    content = PostContent.objects.get(slug="devlog-7", language="en")
    draft = Version.objects.get_for_content(content).copy(user)
    draft.content.post_text = "<p>An unfinished devlog.</p>"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished edited draft"):
        call_command("seed_stories", username=user.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Image.objects.count() == 0
