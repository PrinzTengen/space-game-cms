"""Native Stories rendering, editorial controls and version-safe installation."""

from http import HTTPStatus

import pytest
from cms.models import PageContent
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_stories.models import LatestPostsPlugin
from djangocms_stories.models import Post
from djangocms_stories.models import PostCategory
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def stories_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    return user


def homepage(lang="en"):
    return PageContent.objects.get(page__is_home=True, language=lang)


def latest(content):
    plugin = content.get_placeholders().get(slot="latest").get_plugins().get()
    return plugin.get_plugin_instance()[0]


def test_home_uses_native_latest_entries_in_both_languages(stories_site, client):
    for lang, heading in [
        ("en", "Fresh from development"),
        ("de", "Neu aus der Entwicklung"),
    ]:
        instance = latest(homepage(lang))
        assert isinstance(instance, LatestPostsPlugin)
        assert instance.plugin_type == "BlogLatestEntriesPlugin"
        assert instance.latest_posts == 3  # noqa: PLR2004
        client.post(reverse("set_language"), {"language": lang, "next": "/"})
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK
        assert heading.encode() in response.content
        assert response.content.count(b'class="sg-window sg-post-card"') == 3  # noqa: PLR2004
        assert response.content.count(b"data-stories-latest") == 1


def test_native_controls_filter_and_copy_categories_and_tags(stories_site, client):
    draft = Version.objects.get_for_content(homepage()).copy(stories_site)
    instance = latest(draft.content)
    instance.latest_posts = 1
    instance.tags.add("devlog")
    category = PostCategory.objects.create(
        app_config=instance.app_config,
        name="Development",
        slug="development",
    )
    instance.categories.add(category)
    post = Post.objects.filter(tags__slug="devlog").first()
    post.categories.add(category)
    instance.save()
    client.force_login(stories_site)
    response = client.get(
        reverse("admin:cms_placeholder_edit_plugin", args=[instance.pk]),
    )
    assert response.status_code == HTTPStatus.OK
    for field in ["app_config", "latest_posts", "categories", "tags"]:
        assert f'id="id_{field}"'.encode() in response.content
    draft.publish(stories_site)
    response = client.get("/")
    assert response.content.count(b'class="sg-window sg-post-card"') == 1
    assert b'data-post-kind="devlog"' in response.content
    copy = Version.objects.get_for_content(homepage()).copy(stories_site)
    assert list(latest(copy.content).tags.values_list("name", flat=True)) == ["devlog"]
    assert list(latest(copy.content).categories.values_list("pk", flat=True)) == [
        category.pk,
    ]


def test_plugin_hides_draft_articles(stories_site, client):
    post = Post.objects.create(
        author=stories_site,
        app_config=latest(homepage()).app_config,
    )
    content = PostContent.objects.with_user(stories_site).create(
        post=post,
        language="en",
        title="Unpublished launch plans",
        slug="private-plan",
    )
    assert Version.objects.get_for_content(content).state == "draft"
    assert b"Unpublished launch plans" not in client.get("/").content


def test_install_stories_handles_new_placeholder_and_unchanged_draft(stories_site):
    home = homepage()
    home.get_placeholders().get(slot="latest").delete()
    draft = Version.objects.get_for_content(home).copy(stories_site)
    call_command("install_home_stories", username=stories_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert isinstance(latest(homepage()), LatestPostsPlugin)
    count = Version.objects.count()
    call_command("install_home_stories", username=stories_site.username)
    assert Version.objects.count() == count


def test_install_stories_preserves_edited_draft(stories_site):
    home = homepage()
    home.get_placeholders().get(slot="latest").get_plugins().delete()
    draft = Version.objects.get_for_content(home).copy(stories_site)
    draft.content.title = "An unfinished homepage"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_home_stories", username=stories_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
