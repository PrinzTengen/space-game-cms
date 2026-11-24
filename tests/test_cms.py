"""Integration coverage for the CMS alongside the existing Django applications."""

from http import HTTPStatus

import pytest
from cms.api import create_page
from cms.models import Page
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client
from django.urls import reverse
from djangocms_cookie_love.models import CookieConsentConfig
from djangocms_cookie_love.models import CookieGroup
from djangocms_frontend.models import FrontendUIItem
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version
from filer.models import Image

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def cms_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def test_bootstrap_preserves_published_content(cms_site):
    page_ids = list(Page.objects.values_list("pk", flat=True))
    version_ids = list(Version.objects.values_list("pk", flat=True))
    call_command("bootstrap_cms", username=cms_site.username)
    assert list(Page.objects.values_list("pk", flat=True)) == page_ids
    assert list(Version.objects.values_list("pk", flat=True)) == version_ids


def test_bootstrap_requires_existing_superuser():
    with pytest.raises(CommandError, match="active superuser"):
        call_command("bootstrap_cms", username="missing")
    assert not Page.objects.exists()


@pytest.mark.parametrize("url", ["/", "/about/", "/stories/"])
def test_cms_pages_and_stories_render(cms_site, client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert b"Space Game" in response.content
    assert b"/download/" in response.content
    assert b"/stories/" in response.content


def test_drafts_are_hidden_from_visitors(cms_site, client):
    create_page(
        "Unpublished",
        "cms/default.html",
        "en",
        slug="unpublished",
        created_by=cms_site,
    )
    assert client.get("/unpublished/").status_code == HTTPStatus.NOT_FOUND


def header_navigation(response):
    return response.content.split(b'<ul class="sg-nav">', 1)[1].split(b"</nav>")[0]


def test_navigation_uses_english_fallback_for_german_visitors(cms_site, client):
    response = client.get("/", HTTP_ACCEPT_LANGUAGE="de-DE,de;q=0.9")
    assert response.status_code == HTTPStatus.OK
    navigation = header_navigation(response)
    assert b'href="/stories/"' in navigation
    assert b">Stories</a>" in navigation


def test_navigation_follows_the_published_cms_page_tree(cms_site, client):
    def add_page(slug, *, parent=None, visible=True, publish=True):
        page = create_page(
            slug.title(),
            "cms/default.html",
            "en",
            slug=slug,
            menu_title=f"Menu {slug}",
            parent=parent,
            in_navigation=visible,
            created_by=cms_site,
        )
        if publish:
            content = PageContent.admin_manager.get(page=page, language="en")
            Version.objects.get_for_content(content).publish(cms_site)
        return page

    parent = add_page("guide")
    child = add_page("parts", parent=parent)
    add_page("engines", parent=child)
    add_page("hidden", parent=parent, visible=False)
    add_page("draft", parent=parent, publish=False)

    response = client.get("/guide/parts/engines/")
    assert response.status_code == HTTPStatus.OK
    navigation = header_navigation(response)
    submenu_id = f"sg-subnav-{parent.pk}".encode()
    assert b'aria-controls="' + submenu_id + b'"' in navigation
    assert b'aria-label="Subpages of Menu guide"' in navigation
    top_level, submenu = navigation.split(b'id="' + submenu_id + b'"', 1)
    assert b'href="/guide/"' in top_level
    assert b'href="/guide/parts/"' in submenu
    assert b'href="/guide/parts/engines/"' in submenu
    assert b'aria-current="page">Menu engines</a>' in submenu
    assert b"/guide/hidden/" not in navigation
    assert b"/guide/draft/" not in navigation


def test_stories_apphook_lists_published_posts(cms_site, client):
    post = Post.objects.create(
        author=cms_site,
        app_config=StoriesConfig.objects.get(namespace="stories"),
    )
    content = PostContent.objects.with_user(cms_site).create(
        post=post,
        language="en",
        title="First mission",
        slug="first-mission",
    )
    assert b"First mission" not in client.get("/stories/").content
    Version.objects.get_for_content(content).publish(cms_site)
    response = client.get("/stories/")
    assert response.status_code == HTTPStatus.OK
    assert b"First mission" in response.content
    assert b"First mission" not in header_navigation(response)
    response = client.get(content.get_absolute_url())
    assert response.status_code == HTTPStatus.OK
    assert b"First mission" in response.content


def test_cookie_banner_and_consent_with_csrf(cms_site):
    config = CookieConsentConfig.objects.create()
    CookieGroup.objects.create(
        config=config,
        name="Essential",
        slug="essential",
        is_required=True,
    )
    client = Client(enforce_csrf_checks=True)
    response = client.get("/")
    assert b'id="cookie-love-banner"' in response.content
    token = response.context["csrf_token"]
    response = client.post(
        reverse("cookie_love:api_consent"),
        data={"accepted_groups": [], "consent_method": "banner_reject"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=str(token),
    )
    assert response.status_code == HTTPStatus.CREATED, response.content
    assert response.json()["accepted_groups"] == ["essential"]
    assert response.cookies["cookie_love_consent"]["httponly"]
    status = client.get(reverse("cookie_love:api_consent"))
    assert status.json()["has_consent"] is True


def test_application_routes_take_precedence(cms_site, client):
    assert client.get(reverse("account_login")).status_code == HTTPStatus.OK
    assert client.get(reverse("api:user-list")).status_code in {
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.FORBIDDEN,
    }
    client.force_login(cms_site)
    assert client.get(reverse("admin:index")).status_code == HTTPStatus.OK


def get_home_hero_content():
    return PageContent.objects.get(page__is_home=True, language="en")


def test_hero_is_editable_frontend_component(cms_site, rf, client):
    content = get_home_hero_content()
    hero = (
        content.get_placeholders()
        .get(slot="hero")
        .get_plugins()
        .get(parent__isnull=True)
    )
    instance, _ = hero.get_plugin_instance()
    assert isinstance(instance, FrontendUIItem)
    request = rf.get("/")
    request.user = cms_site
    plugin_class = plugin_pool.get_plugin("SpaceGameHeroPlugin")
    plugin = plugin_class(plugin_class.model, admin.site)
    form = plugin.get_form(request, obj=instance, change=True)(instance=instance)
    assert form.initial["title"] == "Chart the unknown."
    assert {"image", "image_alt"} <= set(form.fields)
    draft = Version.objects.get_for_content(content).copy(cms_site)
    draft_hero = (
        draft.content.get_placeholders()
        .get(slot="hero")
        .get_plugins()
        .get(parent__isnull=True)
    )
    client.force_login(cms_site)
    response = client.get(
        reverse("admin:cms_placeholder_edit_plugin", args=[draft_hero.pk]),
    )
    assert response.status_code == HTTPStatus.OK
    assert b'id="id_title"' in response.content
    assert b'id="id_image"' in response.content


def test_hero_copy_and_publish_custom_content(cms_site, client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    # A small valid GIF is sufficient to exercise Filer image selection/storage.
    image = Image.objects.create(
        file=SimpleUploadedFile(
            "hero.gif",
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        ),
        owner=cms_site,
        original_filename="hero.gif",
    )
    content = get_home_hero_content()
    draft = Version.objects.get_for_content(content).copy(cms_site)
    instance, _ = (
        draft.content.get_placeholders()
        .get(slot="hero")
        .get_plugins()
        .get(parent__isnull=True)
        .get_plugin_instance()
    )
    assert instance.config["title"] == "Chart the unknown."
    about = Page.objects.get(reverse_id="about")
    instance.config.update(
        title="Mission <One>",
        image={"model": "filer.image", "pk": image.pk},
        image_alt="A new mission",
    )
    instance.save()
    buttons = list(instance.get_children().order_by("position"))
    button = buttons[0].get_plugin_instance()[0]
    button.config.update(
        name="About our mission",
        link={"internal_link": f"cms.page:{about.pk}"},
    )
    button.save()
    buttons[1].delete()
    draft.publish(cms_site)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert b"Mission &lt;One&gt;" in response.content
    assert image.url.encode() in response.content
    assert b'width="1"' in response.content
    assert b'href="/about/"' in response.content
    assert b"btn btn-outline-light" not in response.content


def test_install_hero_uses_unchanged_empty_draft(cms_site):
    content = get_home_hero_content()
    content.get_placeholders().get(slot="hero").get_plugins().delete()
    draft = Version.objects.get_for_content(content).copy(cms_site)
    call_command("install_home_hero", username=cms_site.username)
    draft = Version.objects.get(pk=draft.pk)
    assert draft.state == "published"
    hero = get_home_hero_content().get_placeholders().get(slot="hero")
    assert (
        hero.get_plugins().get(parent__isnull=True).plugin_type == "SpaceGameHeroPlugin"
    )
    count = Version.objects.count()
    call_command("install_home_hero", username=cms_site.username)
    assert Version.objects.count() == count


def test_install_hero_preserves_unpublished_changes(cms_site):
    content = get_home_hero_content()
    content.get_placeholders().get(slot="hero").get_plugins().delete()
    published = Version.objects.get_for_content(content)
    draft = published.copy(cms_site)
    draft.content.title = "An unpublished change"
    draft.content.save()
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_home_hero", username=cms_site.username)
    draft = Version.objects.get(pk=draft.pk)
    published = Version.objects.get(pk=published.pk)
    assert draft.state == "draft"
    assert published.state == "published"
    assert draft.content.title == "An unpublished change"
