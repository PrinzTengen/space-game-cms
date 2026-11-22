"""Published Contributor pages, shared cards and editorial form validation."""

from http import HTTPStatus

import pytest
from cms.api import add_plugin
from cms.api import create_page
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from django.core.management import call_command
from django.urls import reverse
from djangocms_versioning.models import Version

from space_game.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_contributor_page_shares_published_cards_in_both_languages(client):
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    page = create_page(
        "Contributor",
        "cms/default.html",
        "de",
        slug="contributor",
        created_by=user,
        in_navigation=True,
    )
    original = PageContent.admin_manager.get(page=page, language="de")
    Version.objects.get_for_content(original).publish(user)
    call_command("install_contributors", username=user.username)
    published = PageContent.objects.get(page=page, language="de")
    draft = Version.objects.get_for_content(published).copy(user)
    slot = draft.content.placeholders.get(slot="contributors")
    group = slot.get_plugins().get(plugin_type="SpaceGameContributorsPlugin")
    card = add_plugin(
        slot,
        "SpaceGameContributorPlugin",
        "de",
        target=group,
        config={
            "name": "Mira Keller",
            "bio_de": "Entwickelt Systeme <im Spiel>.",
            "bio_en": "Develops game systems.",
            "github_url": "https://github.com/example",
        },
    )
    add_plugin(
        slot,
        "SpaceGameContributorRolePlugin",
        "de",
        target=card,
        config={"preset": "game"},
    )

    client.force_login(user)
    editor = client.get(reverse("admin:cms_placeholder_edit_plugin", args=[card.pk]))
    assert editor.status_code == HTTPStatus.OK
    assert b"js/contributor-bio.js" in editor.content
    assert b'data-contributor-counter="id_bio_de-count"' in editor.content
    client.logout()
    assert b"Mira Keller" not in client.get("/contributor/").content
    draft.publish(user)
    for lang, hero, bio, role in [
        (
            "de",
            "Die Menschen hinter Space Game",
            "Entwickelt Systeme &lt;im Spiel&gt;.",
            "Spielentwicklung",
        ),
        (
            "en",
            "Meet the people behind Space Game",
            "Develops game systems.",
            "Game Development",
        ),
    ]:
        client.post(
            reverse("set_language"), {"language": lang, "next": "/contributor/"},
        )
        response = client.get("/contributor/")
        assert response.status_code == HTTPStatus.OK
        assert b"space-hero-compact" in response.content
        assert hero.encode() in response.content
        assert bio.encode() in response.content
        assert role.encode() in response.content
        assert b"Mira Keller" in response.content
        assert b"https://github.com/example" in response.content

    versions = Version.objects.count()
    call_command("install_contributors", username=user.username)
    assert Version.objects.count() == versions


def test_contributor_bio_form_has_a_limit_and_counter():
    plugin = plugin_pool.get_plugin("SpaceGameContributorPlugin")
    long_bio = "A" * 501
    form = plugin.form(
        data={"name": "Mira Keller", "bio_de": long_bio, "bio_en": long_bio},
    )
    assert not form.is_valid()
    assert form.errors.as_data()["bio_de"][0].code == "max_length"
    assert form.errors.as_data()["bio_en"][0].code == "max_length"
    html = str(plugin.form(initial={"bio_de": "ABC"})["bio_de"])
    assert 'maxlength="500"' in html
    assert 'aria-describedby="id_bio_de-count"' in html
    assert "data-contributor-length>3</span> / 500" in html
    assert "js/contributor-bio.js" in str(plugin.form().media)
