"""Native CMS import, bilingual pages and real download authorization."""

from datetime import timedelta
from http import HTTPStatus

import pytest
from allauth.socialaccount.models import SocialAccount
from cms.models import PageContent
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils import timezone
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.theme.design import published_posts
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def design_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    return user


def test_reference_pages_and_posts_are_available_in_both_languages(design_site, client):
    for lang, title in [
        ("de", "Kartiere das Unbekannte."),
        ("en", "Chart the unknown."),
    ]:
        headers = {"HTTP_ACCEPT_LANGUAGE": lang}
        client.post(reverse("set_language"), {"language": lang, "next": "/"})
        home = client.get("/", **headers)
        assert home.status_code == HTTPStatus.OK
        assert title.encode() in home.content
        assert b"build/design-system/hero-keyart.png" in home.content
        assert b"build/design-system/cta-station.png" in home.content
        for path in ["/stories/", "/download/", "/faq/"]:
            assert client.get(path, **headers).status_code == HTTPStatus.OK
        entries = list(published_posts(lang))
        assert len(entries) == 5  # noqa: PLR2004
        for entry in entries:
            response = client.get(entry.get_absolute_url(), **headers)
            assert response.status_code == HTTPStatus.OK
            assert entry.title.encode() in response.content
            assert b"sg-article-body" in response.content
            assert entry.post_text.split("</p>")[0].encode() in response.content


def test_design_import_is_idempotent_and_keeps_edits(design_site):
    original_count = Version.objects.count()
    home = PageContent.objects.get(page__is_home=True, language="en")
    draft = Version.objects.get_for_content(home).copy(design_site)
    draft.content.title = "An ongoing editorial change"
    draft.content.save()
    call_command("apply_design_system", username=design_site.username)
    assert Version.objects.count() == original_count + 1
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert draft.content.title == "An ongoing editorial change"


def test_first_design_import_preserves_an_edited_draft():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("bootstrap_cms", username=user.username)
    home = PageContent.objects.get(page__is_home=True, language="en")
    draft = Version.objects.get_for_content(home).copy(user)
    draft.content.title = "Do not publish this"
    draft.content.save()
    with pytest.raises(CommandError, match="edited unpublished draft"):
        call_command("apply_design_system", username=user.username)
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert not PostContent.objects.exists()


def test_future_and_expired_posts_are_hidden(design_site):
    content = published_posts("en").first()
    content.post.date_published = timezone.now() + timedelta(days=1)
    content.post.save()
    assert not published_posts("en").filter(pk=content.pk).exists()
    content.post.date_published = timezone.now() - timedelta(days=2)
    content.post.date_published_end = timezone.now() - timedelta(days=1)
    content.post.save()
    assert not published_posts("en").filter(pk=content.pk).exists()


def test_download_requires_server_side_discord_identity(client, settings):
    settings.SG_LAUNCHER_URLS = {"win": "https://example.com/launcher.exe"}
    response = client.get("/launcher/win/")
    assert response.status_code == HTTPStatus.FOUND
    assert "/accounts/login/" in response.url
    user = UserFactory()
    client.force_login(user)
    assert client.get("/launcher/win/").status_code == HTTPStatus.FORBIDDEN
    SocialAccount.objects.create(user=user, provider="discord", uid="12345")
    response = client.get("/launcher/win/")
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == "https://example.com/launcher.exe"
    assert client.get("/launcher/mac/").status_code == HTTPStatus.NOT_FOUND
    settings.SG_LAUNCHER_URLS = {"win": "http://example.com/launcher.exe"}
    assert client.get("/launcher/win/").status_code == HTTPStatus.NOT_FOUND


def test_missing_discord_configuration_is_honest(design_site, client, settings):
    settings.SG_DISCORD_CLIENT_ID = ""
    response = client.get("/download/", HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == HTTPStatus.OK
    assert b"Discord sign-in is being prepared" in response.content
    assert b"sg-auth" not in response.content
