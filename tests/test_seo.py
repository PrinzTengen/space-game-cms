"""sitemap.xml, robots.txt and llms.txt."""

from datetime import timedelta
from http import HTTPStatus

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.utils.timezone import now
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def cms_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def publish_story(user, title, slug, *, publish=True, **post_fields):
    post = Post.objects.create(
        author=user,
        app_config=StoriesConfig.objects.get(namespace="stories"),
        **post_fields,
    )
    content = PostContent.objects.with_user(user).create(
        post=post,
        language="en",
        title=title,
        slug=slug,
        meta_description=f"About {title}",
    )
    if publish:
        Version.objects.get_for_content(content).publish(user)
    return content


def test_sitemap_lists_published_pages_and_stories(cms_site, client):
    published = publish_story(cms_site, "First mission", "first-mission")
    publish_story(cms_site, "Secret draft", "secret-draft", publish=False)
    publish_story(
        cms_site,
        "Future launch",
        "future-launch",
        date_published=now() + timedelta(days=3),
    )

    origin = f"http://{Site.objects.get_current().domain}"
    response = client.get("/sitemap.xml")
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"].startswith("application/xml")
    body = response.content.decode()
    assert f"<loc>{origin}/</loc>" in body
    assert f"<loc>{origin}/about/</loc>" in body
    assert f"<loc>{origin}/stories/</loc>" in body
    assert f"<loc>{origin}{published.get_absolute_url()}</loc>" in body
    assert "secret-draft" not in body
    assert "future-launch" not in body
    assert body.count(f"<loc>{origin}/about/</loc>") == 1


def test_robots_txt_points_to_the_sitemap(client, settings):
    settings.ADMIN_URL = "hidden-control-room/"
    origin = f"http://{Site.objects.get_current().domain}"
    response = client.get("/robots.txt")
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "text/plain; charset=utf-8"
    body = response.content.decode()
    assert body.startswith("User-agent: *\n")
    assert "Disallow: /api/\n" in body
    assert f"Sitemap: {origin}/sitemap.xml" in body
    assert "hidden-control-room" not in body


def test_llms_txt_summarises_pages_and_stories(cms_site, client):
    story = publish_story(cms_site, "First mission", "first-mission")
    publish_story(cms_site, "Secret draft", "secret-draft", publish=False)

    origin = f"http://{Site.objects.get_current().domain}"
    response = client.get("/llms.txt")
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "text/plain; charset=utf-8"
    body = response.content.decode()
    assert body.startswith("# Space Game\n\n> ")
    assert "## Pages" in body
    assert f"]({origin}/about/)" in body
    assert "## Stories" in body
    assert (
        f"- [First mission]({origin}{story.get_absolute_url()}): About First mission"
    ) in body
    assert "Secret draft" not in body
