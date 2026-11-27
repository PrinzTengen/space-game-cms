"""Standalone FAQ groups and versioned support-page content."""

import json
import re
from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from cms.api import add_plugin
from cms.models import PageContent
from cms.toolbar.utils import get_object_edit_url
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils.html import escape
from djangocms_versioning.models import Version

from space_game.theme.design import catalog
from space_game.theme.faq import FAQ_PLUGIN_TYPES
from space_game.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

LD_JSON = re.compile(rb'<script type="application/ld\+json">(.*?)</script>', re.S)


def faq_schemas(response):
    blocks = [json.loads(raw) for raw in LD_JSON.findall(response.content)]
    return [block for block in blocks if block.get("@type") == "FAQPage"]


@pytest.fixture
def faq_site():
    user = UserFactory(is_superuser=True, is_staff=True)
    call_command("apply_design_system", username=user.username)
    return user


def support(lang="en"):
    return PageContent.objects.get(page__reverse_id="faq", language=lang)


def plugins(content, slot):
    return [
        p.get_plugin_instance()[0]
        for p in content.get_placeholders()
        .get(slot=slot)
        .get_plugins()
        .order_by("position")
    ]


@pytest.mark.parametrize("lang", ["en", "de"])
def test_support_page_uses_bilingual_plugin_content(faq_site, client, lang):
    content = support(lang)
    kinds = {
        p.plugin_type
        for placeholder in content.placeholders.all()
        for p in placeholder.get_plugins()
    }
    assert kinds == set(FAQ_PLUGIN_TYPES)
    assert len(plugins(content, "faq")) == 6  # noqa: PLR2004
    assert len(plugins(content, "system_requirements")) == 7  # noqa: PLR2004
    client.post(reverse("set_language"), {"language": lang, "next": "/faq/"})
    response = client.get("/faq/")
    assert response.status_code == HTTPStatus.OK
    for question, answer in catalog()["faq"][lang]:
        assert escape(question).encode() in response.content
        assert escape(answer).encode() in response.content
    group = plugins(content, "faq")[0]
    assert f'name="space-game-faq-{group.pk}"'.encode() in response.content
    assert response.content.count(b" open>") == 1


def test_faq_groups_work_independently_on_another_page(faq_site, client):
    home = PageContent.objects.get(page__is_home=True, language="en")
    draft = Version.objects.get_for_content(home).copy(faq_site)
    placeholder = draft.content.get_placeholders().get(slot="content")
    groups = []
    for title in ["Flight questions", "Trading questions"]:
        group = add_plugin(
            placeholder,
            "SpaceGameFAQPlugin",
            "en",
            config={"title": title, "single_open": True},
        )
        add_plugin(
            placeholder,
            "SpaceGameFAQItemPlugin",
            "en",
            target=group,
            config={
                "question": f"How does {title} work?",
                "answer": "A standalone answer.",
                "initially_open": True,
            },
        )
        groups.append(group)
    draft.publish(faq_site)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    for group in groups:
        assert group.config["title"].encode() in response.content
        assert f'name="space-game-faq-{group.pk}"'.encode() in response.content
    assert response.content.count(b"data-faq ") == 2  # noqa: PLR2004


@pytest.mark.parametrize("count", [0, 1, 7])
def test_question_count_is_managed_entirely_by_plugins(faq_site, client, count):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    group = plugins(draft.content, "faq")[0]
    group.get_children().delete()
    for index in range(count):
        add_plugin(
            group.placeholder,
            "SpaceGameFAQItemPlugin",
            "en",
            target=group,
            config={
                "question": f"Custom question {index}",
                "answer": "Custom answer",
                "initially_open": False,
            },
        )
    draft.publish(faq_site)
    response = client.get("/faq/")
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b"<summary>") == count
    assert b"Do I need a Discord account" not in response.content


def test_native_forms_edit_every_support_module_and_expand_questions(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    client.force_login(faq_site)
    forms = [
        (plugins(draft.content, "support_header")[0], ["eyebrow", "title", "subtitle"]),
        (
            plugins(draft.content, "system_requirements")[0],
            ["title", "component_label", "minimum_label", "recommended_label", "note"],
        ),
        (
            plugins(draft.content, "system_requirements")[1],
            ["title", "minimum", "recommended"],
        ),
        (plugins(draft.content, "faq")[0], ["title", "description", "single_open"]),
        (plugins(draft.content, "faq")[1], ["question", "answer", "initially_open"]),
    ]
    for instance, fields in forms:
        response = client.get(
            reverse("admin:cms_placeholder_edit_plugin", args=[instance.pk]),
        )
        assert response.status_code == HTTPStatus.OK
        for field in fields:
            assert f'id="id_{field}"'.encode() in response.content
    item = plugins(draft.content, "faq")[1]
    assert item.get_short_description() == item.config["question"]
    response = client.get(get_object_edit_url(draft.content))
    assert response.status_code == HTTPStatus.OK
    assert response.content.count(b" open>") == 5  # noqa: PLR2004
    assert b'name="space-game-faq-' not in response.content


def test_cms_saves_question_and_answer_only_after_publication(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    item = plugins(draft.content, "faq")[1]
    client.force_login(faq_site)
    edit_url = reverse("admin:cms_placeholder_edit_plugin", args=[item.pk])
    edit_url += "?" + urlencode({"cms_path": get_object_edit_url(draft.content)})
    response = client.post(
        edit_url,
        {
            "question": "My <question>",
            "answer": "Paragraph one.\n\n<script>alert(1)</script>",
            "initially_open": "on",
            "_save": "Save",
        },
    )
    assert response.status_code == HTTPStatus.OK
    client.logout()
    assert b"My &lt;question&gt;" not in client.get("/faq/").content
    draft.publish(faq_site)
    response = client.get("/faq/")
    assert b"My &lt;question&gt;" in response.content
    assert b"<p>Paragraph one.</p>" in response.content
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.content
    assert b"<script>alert(1)</script>" not in response.content


def test_removing_faq_does_not_restore_hardcoded_questions(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    draft.content.get_placeholders().get(slot="faq").get_plugins().delete()
    draft.publish(faq_site)
    response = client.get("/faq/")
    assert b"data-faq" not in response.content
    assert b"Do I need a Discord account" not in response.content
    assert b"System requirements" in response.content


def test_faq_installer_is_idempotent_and_preserves_user_drafts(faq_site):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    item = plugins(draft.content, "faq")[1]
    item.config["answer"] = "Unfinished answer"
    item.save()
    count = Version.objects.count()
    call_command("install_faq_plugins", username=faq_site.username)
    assert Version.objects.count() == count
    assert Version.objects.get(pk=draft.pk).state == "draft"
    assert plugins(draft.content, "faq")[1].config["answer"] == "Unfinished answer"


@pytest.mark.parametrize("edited", [False, True])
def test_legacy_conversion_protects_edited_drafts(faq_site, edited):
    content = support()
    content.placeholders.exclude(slot="content").delete()
    draft = Version.objects.get_for_content(content).copy(faq_site)
    if edited:
        draft.content.title = "Unfinished page"
        draft.content.save()
        with pytest.raises(CommandError, match="unpublished edited draft"):
            call_command("install_faq_plugins", username=faq_site.username)
        assert Version.objects.get(pk=draft.pk).state == "draft"
        assert Version.objects.get_for_content(content).state == "published"
    else:
        call_command("install_faq_plugins", username=faq_site.username)
        assert Version.objects.get(pk=draft.pk).state == "published"
        assert len(plugins(support(), "faq")) == 6  # noqa: PLR2004


def test_legacy_conversion_preserves_extra_page_content(faq_site, client):
    content = support()
    content.placeholders.exclude(slot="content").delete()
    add_plugin(
        content.get_placeholders().get(slot="content"),
        "TextPlugin",
        "en",
        body="<p>Additional support information.</p>",
    )
    call_command("install_faq_plugins", username=faq_site.username)
    assert b"Additional support information." in client.get("/faq/").content


@pytest.mark.parametrize("lang", ["en", "de"])
def test_support_page_publishes_faq_schema(faq_site, client, lang):
    client.post(reverse("set_language"), {"language": lang, "next": "/faq/"})
    response = client.get("/faq/")
    [schema] = faq_schemas(response)
    assert schema["@context"] == "https://schema.org"
    assert [
        (entry["@type"], entry["name"], entry["acceptedAnswer"]["text"])
        for entry in schema["mainEntity"]
    ] == [("Question", q, a) for q, a in catalog()["faq"][lang]]


def test_faq_groups_share_one_schema_and_escape_markup(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    group = plugins(draft.content, "faq")[0]
    group.get_children().delete()
    placeholder = draft.content.get_placeholders().get(slot="content")
    second = add_plugin(placeholder, "SpaceGameFAQPlugin", "en", config={})
    for target, question in [(group, "First?"), (second, "Second </script>?")]:
        add_plugin(
            target.placeholder,
            "SpaceGameFAQItemPlugin",
            "en",
            target=target,
            config={"question": question, "answer": "<b>Yes</b> & no"},
        )
    draft.publish(faq_site)
    response = client.get("/faq/")
    [schema] = faq_schemas(response)
    assert [entry["name"] for entry in schema["mainEntity"]] == [
        "First?",
        "Second </script>?",
    ]
    assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "<b>Yes</b> & no"
    assert b"Second </script>" not in response.content


def test_pages_without_questions_have_no_faq_schema(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    draft.content.get_placeholders().get(slot="faq").get_plugins().delete()
    draft.publish(faq_site)
    assert faq_schemas(client.get("/faq/")) == []
    assert faq_schemas(client.get("/")) == []


def test_edit_mode_has_no_faq_schema(faq_site, client):
    draft = Version.objects.get_for_content(support()).copy(faq_site)
    client.force_login(faq_site)
    response = client.get(get_object_edit_url(draft.content))
    assert response.status_code == HTTPStatus.OK
    assert faq_schemas(response) == []
