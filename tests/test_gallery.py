"""Gallery nesting, images, editing and versioned installation."""

from http import HTTPStatus

import pytest
from cms.api import add_plugin
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from cms.toolbar.utils import get_object_edit_url
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from djangocms_frontend.models import FrontendUIItem
from djangocms_versioning.models import Version
from filer.models import Image

from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def gallery_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    return user


def homepage():
    return PageContent.objects.get(page__is_home=True, language="en")


def gallery(content):
    return (
        content.get_placeholders()
        .get(slot="gallery")
        .get_plugins()
        .get(plugin_type="SpaceGameGalleryPlugin")
    )


def test_gallery_is_saved_below_cta(gallery_site, client):
    group = gallery(homepage())
    instance, _ = group.get_plugin_instance()
    assert isinstance(instance, FrontendUIItem)
    children = list(group.get_children().order_by("position"))
    assert len(children) == 2  # noqa: PLR2004
    assert {child.plugin_type for child in children} == {"SpaceGameGalleryImagePlugin"}
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    html = response.content.decode()
    assert html.index("space-callout") < html.index("data-gallery\n")
    assert html.count('class="gallery-slide"') == 2  # noqa: PLR2004
    assert "Meridian / Low orbit" in html
    assert "Märzbach / Solar drift" in html
    assert "01_meridian_nah_planet.png" in html
    assert "09_maerzbach_vor_nebel_sonne.png" in html


def test_gallery_nesting_and_edit_dialog(gallery_site, client):
    content = homepage()
    parent = plugin_pool.get_plugin("SpaceGameGalleryPlugin")
    child = plugin_pool.get_plugin("SpaceGameGalleryImagePlugin")
    assert parent.get_child_classes("gallery", content) == [
        "SpaceGameGalleryImagePlugin",
    ]
    assert child.get_parent_classes("gallery", content) == ["SpaceGameGalleryPlugin"]
    assert child.require_parent is True
    draft = Version.objects.get_for_content(content).copy(gallery_site)
    group = gallery(draft.content)
    client.force_login(gallery_site)
    for plugin, fields in [
        (group, ["title", "eyebrow", "description"]),
        (
            group.get_children().first(),
            ["image", "image_alt", "title", "default_image"],
        ),
    ]:
        response = client.get(
            reverse("admin:cms_placeholder_edit_plugin", args=[plugin.pk]),
        )
        assert response.status_code == HTTPStatus.OK
        for field in fields:
            assert f'id="id_{field}"'.encode() in response.content


def test_gallery_image_requires_an_image_source():
    plugin = plugin_pool.get_plugin("SpaceGameGalleryImagePlugin")
    instance = plugin.model().initialize_from_form(plugin.form)
    form = plugin.form(
        data={"image_alt": "A space station", "default_image": ""},
        instance=instance,
    )
    assert not form.is_valid()
    assert "image" in form.errors
    form = plugin.form(
        data={"image_alt": "A space station", "default_image": "meridian"},
        instance=instance,
    )
    assert form.is_valid(), form.errors


def test_gallery_editor_uses_content_language(gallery_site, client):
    draft = Version.objects.get_for_content(homepage()).copy(gallery_site)
    client.force_login(gallery_site)
    response = client.get(
        get_object_edit_url(draft.content),
        HTTP_ACCEPT_LANGUAGE="de-DE,de;q=0.9",
    )
    assert response.status_code == HTTPStatus.OK
    assert b"data-gallery-edit-mode" in response.content
    assert b"Meridian / Low orbit" in response.content


def test_gallery_filer_image_and_caption_are_versioned(
    gallery_site,
    client,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = tmp_path
    image = Image.objects.create(
        file=SimpleUploadedFile(
            "gallery.gif",
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        ),
        owner=gallery_site,
        original_filename="gallery.gif",
    )
    draft = Version.objects.get_for_content(homepage()).copy(gallery_site)
    instance, _ = gallery(draft.content).get_children().first().get_plugin_instance()
    instance.config.update(
        image={"model": "filer.image", "pk": image.pk},
        image_alt='Station "One"',
        title="Mission <One>",
    )
    instance.save()
    assert b"Mission &lt;One&gt;" not in client.get("/").content
    draft.publish(gallery_site)
    response = client.get("/")
    assert b"Mission &lt;One&gt;" in response.content
    assert b' alt="Station &quot;One&quot;"' in response.content
    assert image.url.encode() in response.content
    assert b'width="1"' in response.content
    assert b"01_meridian_nah_planet.png" not in response.content


@pytest.mark.parametrize("count", [0, 1, 8])
def test_gallery_preserves_any_number_of_images(gallery_site, client, count):
    draft = Version.objects.get_for_content(homepage()).copy(gallery_site)
    group = gallery(draft.content)
    group.get_children().delete()
    for index in range(count):
        add_plugin(
            group.placeholder,
            "SpaceGameGalleryImagePlugin",
            "en",
            target=group,
            config={
                "default_image": "meridian",
                "image_alt": f"Image {index + 1}",
                "title": f"Scene {index + 1}",
            },
        )
    draft.publish(gallery_site)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b'class="gallery-slide"') == count


def test_install_gallery_is_idempotent(gallery_site):
    content = homepage()
    content.get_placeholders().get(slot="gallery").get_plugins().delete()
    draft = Version.objects.get_for_content(content).copy(gallery_site)
    call_command("install_home_gallery", username=gallery_site.username)
    assert Version.objects.get(pk=draft.pk).state == "published"
    assert gallery(homepage()).get_children().count() == 2  # noqa: PLR2004
    community = homepage().get_placeholders().get(slot="community")
    # The CTA keeps its button as a child plugin; only one CTA may exist.
    assert community.get_plugins().filter(parent__isnull=True).count() == 1
    count = Version.objects.count()
    call_command("install_home_gallery", username=gallery_site.username)
    assert Version.objects.count() == count


def test_install_gallery_preserves_unpublished_cta_changes(gallery_site):
    content = homepage()
    content.get_placeholders().get(slot="gallery").get_plugins().delete()
    original = Version.objects.get_for_content(content)
    draft = original.copy(gallery_site)
    cta, _ = (
        draft.content.get_placeholders()
        .get(slot="community")
        .get_plugins()
        .get(plugin_type="SpaceGameCTAPlugin")
        .get_plugin_instance()
    )
    cta.config["title"] = "An unpublished CTA"
    cta.save()
    with pytest.raises(CommandError, match="unpublished draft"):
        call_command("install_home_gallery", username=gallery_site.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert Version.objects.get(pk=original.pk).state == "published"
    assert (
        not draft.content.get_placeholders().get(slot="gallery").get_plugins().exists()
    )
