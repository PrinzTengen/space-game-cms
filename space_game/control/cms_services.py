# ruff: noqa: C901, PLR0912, PLR0913, PLR0915, PLR0917
from cms.api import add_plugin
from cms.api import create_page
from cms.api import create_page_content
from cms.exceptions import PluginLimitReached
from cms.models import Page
from cms.models import PageContent
from cms.plugin_pool import plugin_pool
from cms.utils import page_permissions
from cms.utils.placeholder import get_placeholder_conf
from cms.utils.placeholder import rescan_placeholders_for_obj
from cms.utils.plugins import has_reached_plugin_limit
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import transaction
from djangocms_frontend.fields import HTMLFormField
from djangocms_frontend.models import FrontendUIItem
from djangocms_stories.models import Post
from djangocms_stories.models import PostContent
from djangocms_versioning.models import Version

from space_game.control.services import audit
from space_game.control.services import clean_form
from space_game.control.services import form_data
from space_game.control.services import request_for
from space_game.control.services import schema


def permit(user, permission):
    if not user.has_perm(permission):
        raise PermissionDenied(permission)


def page_permission(user, content, action="change"):
    permit(user, f"cms.{action}_page")
    if action == "change" and not page_permissions.user_can_change_page(
        user,
        page=content.page,
    ):
        raise PermissionDenied
    if action == "delete" and not page_permissions.user_can_delete_page(
        user,
        page=content.page,
    ):
        raise PermissionDenied


def version_content(kind, pk):
    model = PageContent if kind == "page" else PostContent if kind == "story" else None
    if model is None:
        msg = "Content kind must be page or story."
        raise ValidationError(msg)
    return model.admin_manager.get(pk=pk)


def content_permission(user, content, action="change"):
    if isinstance(content, PageContent):
        page_permission(user, content, action)
    else:
        permit(user, f"djangocms_stories.{action}_post")


def draft_for(user, content):
    content_permission(user, content)
    version = Version.objects.get_for_content(content)
    if not version.check_edit_redirect.as_bool(user):
        raise PermissionDenied
    if version.state == "draft":
        return content
    ids = version.versionable.for_content_grouping_values(content).values_list(
        "pk",
        flat=True,
    )
    existing = Version.objects.filter(
        content_type=version.content_type,
        object_id__in=ids,
        state="draft",
    ).first()
    if existing:
        if not existing.check_edit_redirect.as_bool(user):
            raise PermissionDenied
        return existing.content
    return version.copy(user).content


def content_info(content):
    version = Version.objects.get_for_content(content)
    result = {
        "id": content.pk,
        "language": content.language,
        "title": content.title,
        "version": version.pk,
        "state": version.state,
    }
    if isinstance(content, PageContent):
        result.update(
            page_id=content.page_id,
            template=content.template,
            url=content.get_absolute_url(),
        )
    else:
        result.update(
            post_id=content.post_id,
            slug=content.slug,
            abstract=content.abstract,
            subtitle=content.subtitle,
            post_text=content.post_text,
            metadata={
                "image_id": content.post.main_image_id,
                "app_config_id": content.post.app_config_id,
                "author_id": content.post.author_id,
                "category_ids": list(
                    content.post.categories.values_list("pk", flat=True),
                ),
                "tags": list(content.post.tags.values_list("name", flat=True)),
                "date_published": content.post.date_published,
                "date_published_end": content.post.date_published_end,
            },
        )
    return result


def delete_versioned_grouper(user, grouper, content_model):
    ids = content_model.admin_manager.filter(
        **{"page" if content_model is PageContent else "post": grouper},
    ).values_list("pk", flat=True)
    versions = Version.objects.filter(
        content_type=ContentType.objects.get_for_model(content_model),
        object_id__in=ids,
    ).order_by("-pk")
    for version in versions:
        if version.state == "draft" and not version.check_discard.as_bool(user):
            raise PermissionDenied
        if version.state == "published":
            if not version.check_unpublish.as_bool(user):
                raise PermissionDenied
            version.unpublish(user)
        version.delete()


@transaction.atomic
def pages(user, action, content_id=None, values=None, language="en", parent_id=None):
    values = values or {}
    if action == "list":
        permit(user, "cms.view_page")
        return [
            content_info(c)
            for c in PageContent.admin_manager.latest_content().filter(
                page__site_id=settings.SITE_ID,
                language=language,
            )
            if page_permissions.user_can_view_page(user, c.page)
        ]
    if action == "create":
        permit(user, "cms.add_page")
        parent = (
            Page.objects.get(pk=parent_id, site_id=settings.SITE_ID)
            if parent_id
            else None
        )
        site = Site.objects.get(pk=settings.SITE_ID)
        can_add = (
            page_permissions.user_can_add_subpage(user, parent, site)
            if parent
            else page_permissions.user_can_add_page(user, site)
        )
        if not can_add:
            raise PermissionDenied
        page = create_page(
            values["title"],
            values.get("template", "cms/default.html"),
            language,
            slug=values.get("slug"),
            parent=parent,
            site=site,
            created_by=user,
            in_navigation=values.get("in_navigation", True),
        )
        content = PageContent.admin_manager.get(page=page, language=language)
    else:
        original = PageContent.admin_manager.get(
            pk=content_id,
            page__site_id=settings.SITE_ID,
        )
        content_permission(
            user,
            original,
            "view" if action == "get" else "delete" if action == "delete" else "change",
        )
        if action == "get":
            return content_info(original)
        if action == "delete":
            target = original.page_id
            tree = [*original.page.get_descendants().order_by("-depth"), original.page]
            for page in tree:
                if not page_permissions.user_can_delete_page(user, page=page):
                    raise PermissionDenied
            for page in tree:
                delete_versioned_grouper(user, page, PageContent)
            audit(user, "pages.delete", target)
            return {"deleted_page": target}
        if action == "translate":
            permit(user, "cms.add_page")
            create_page_content(
                language,
                values.get("title", original.title),
                page=original.page,
                created_by=user,
                slug=values.get("slug"),
                template=original.template,
            )
            content = PageContent.admin_manager.get(
                page=original.page,
                language=language,
                versions__state="draft",
            )
        elif action == "update":
            content = draft_for(user, original)
            allowed = {
                "title",
                "page_title",
                "menu_title",
                "meta_description",
                "template",
                "in_navigation",
            }
            if set(values) - allowed:
                msg = "Unsupported page fields."
                raise ValidationError(msg)
            if "template" in values and values["template"] not in dict(
                settings.CMS_TEMPLATES,
            ):
                msg = "Unknown page template."
                raise ValidationError(msg)
            for key, value in values.items():
                setattr(content, key, value)
            content.full_clean()
            content.save()
        else:
            msg = "Unsupported page operation."
            raise ValidationError(msg)
    audit(user, f"pages.{action}", content.pk)
    return content_info(content)


def plugin_info(plugin, user):
    instance, _ = plugin.get_plugin_instance()
    result = {
        "id": plugin.pk,
        "type": plugin.plugin_type,
        "position": plugin.position,
        "parent_id": plugin.parent_id,
        "placeholder_id": plugin.placeholder_id,
    }
    if isinstance(instance, FrontendUIItem):
        result["values"] = instance.config
    elif instance is not None:
        cls = plugin.get_plugin_class()
        form_class = cls(cls.model, admin.site).get_form(request_for(user), instance)
        form = form_class(instance=instance)
        result["values"] = {
            name: list(value.values_list("pk", flat=True))
            if hasattr(value, "values_list")
            else value.pk
            if hasattr(value, "pk")
            else value
            for name, value in form.initial.items()
            if name in form.fields and name not in {"id", "cmsplugin_ptr"}
        }
    return result


def validate_plugin_parent(cls, parent, slot, content):
    if cls.require_parent and parent is None:
        msg = "This plugin requires a parent."
        raise ValidationError(msg)
    if parent:
        parent_admin = parent.get_plugin_class()
        allowed = parent_admin.get_child_classes(slot, page=content, instance=parent)
        if not parent_admin.allow_children or (
            allowed is not None and cls.__name__ not in allowed
        ):
            msg = "Plugin is not allowed under this parent."
            raise ValidationError(msg)
        parents = cls.get_parent_classes(slot, page=content, instance=parent)
        if parents and parent.plugin_type not in parents:
            msg = "Plugin requires a different parent type."
            raise ValidationError(msg)


@transaction.atomic
def plugins(
    user,
    action,
    content_id=None,
    slot=None,
    plugin_type=None,
    plugin_id=None,
    parent_id=None,
    values=None,
    position=None,
):
    if action == "types":
        result = []
        plugin_pool.discover_plugins()
        for cls in plugin_pool.plugins.values():
            label = cls.model._meta.app_label  # noqa: SLF001
            name = cls.model._meta.model_name  # noqa: SLF001
            if user.has_perm(f"{label}.add_{name}") or user.has_perm(
                f"{label}.view_{name}",
            ):
                result.append(
                    {
                        "type": cls.__name__,
                        "name": str(cls.name),
                        "children": cls.allow_children,
                        "fields": schema(
                            cls(cls.model, admin.site).get_form(request_for(user)),
                        ),
                    },
                )
        return result
    content = PageContent.admin_manager.get(
        pk=content_id,
        page__site_id=settings.SITE_ID,
    )
    if action == "list":
        content_permission(user, content, "view")
        return [
            {
                "slot": p.slot,
                "plugins": [
                    plugin_info(item, user)
                    for item in p.get_plugins().order_by("position")
                ],
            }
            for p in content.placeholders.all()
        ]
    # Operate on explicit draft IDs so a published plugin ID can never refer to
    # a different copied child after a page-version copy.
    content_permission(user, content)
    if Version.objects.get_for_content(content).state != "draft":
        msg = "Create a draft first, then list and use the draft's plugin IDs."
        raise ValidationError(msg)
    if not Version.objects.get_for_content(content).check_edit_redirect.as_bool(user):
        raise PermissionDenied
    placeholders = rescan_placeholders_for_obj(content)
    placeholder = placeholders[slot]
    instance = None
    if plugin_id:
        base = placeholder.get_plugins().get(pk=plugin_id, language=content.language)
        instance, plugin_admin = base.get_plugin_instance()
    if action == "delete":
        if not all(
            placeholder.has_delete_plugin_permission(user, child)
            for child in [base, *base.get_descendants()]
        ):
            raise PermissionDenied
        placeholder.delete_plugin(base)
        audit(user, "plugins.delete", plugin_id)
        return {"deleted": plugin_id}
    if action == "move":
        if not placeholder.has_move_plugin_permission(user, base, placeholder):
            raise PermissionDenied
        target = placeholder.get_plugins().get(pk=parent_id) if parent_id else None
        if target and (
            target.pk == base.pk or base.get_descendants().filter(pk=target.pk).exists()
        ):
            msg_0 = "A plugin cannot be moved inside itself."
            raise ValidationError(msg_0)
        validate_plugin_parent(base.get_plugin_class(), target, slot, content)
        if (
            not isinstance(position, int)
            or position < 1
            or position
            > placeholder.get_plugins().filter(language=content.language).count()
        ):
            msg = "Supply an existing positive target position."
            raise ValidationError(msg)
        placeholder.move_plugin(base, target_position=position, target_plugin=target)
        audit(user, "plugins.move", plugin_id)
        return plugin_info(placeholder.get_plugins().get(pk=plugin_id), user)
    if action == "add":
        cls = plugin_pool.get_plugin(plugin_type)
        if not placeholder.has_add_plugin_permission(user, plugin_type):
            raise PermissionDenied
        request = request_for(user)
        configured = get_placeholder_conf("plugins", slot, content.template)
        if configured is not None and plugin_type not in configured:
            msg_0 = "Plugin is not allowed in this placeholder."
            raise ValidationError(msg_0)
        try:
            has_reached_plugin_limit(
                placeholder,
                plugin_type,
                content.language,
                content.template,
            )
        except PluginLimitReached as exc:
            raise ValidationError(str(exc)) from exc
        parent = placeholder.get_plugins().get(pk=parent_id) if parent_id else None
        validate_plugin_parent(cls, parent, slot, content)
        form_class = cls(cls.model, admin.site).get_form(request)
        if set(values or {}) - set(form_class.base_fields):
            msg = "Unknown plugin fields."
            raise ValidationError(msg)
        empty = form_class()
        defaults = {
            name: empty.get_initial_for_field(field, name)
            for name, field in empty.fields.items()
            if field.initial is not None
        }
        form = clean_form(
            form_class(data=form_data({**defaults, **(values or {})}, form_class)),
        )
        config = form.cleaned_data.get("config", {})
        if issubclass(cls.model, FrontendUIItem):
            instance = add_plugin(
                placeholder,
                plugin_type,
                content.language,
                target=parent,
                config=config,
            )
        else:
            fields = {field.name for field in cls.model._meta.concrete_fields}  # noqa: SLF001
            data = {
                key: value
                for key, value in form.cleaned_data.items()
                if key in fields
                and key
                not in {
                    "id",
                    "cmsplugin_ptr",
                    "placeholder",
                    "position",
                    "language",
                    "parent",
                    "plugin_type",
                }
            }
            form.save(commit=False)
            added = add_plugin(
                placeholder,
                plugin_type,
                content.language,
                target=parent,
                **data,
            )
            form.instance = added
            form.save_m2m()
            instance = added
    elif action == "update":
        if not placeholder.has_change_plugin_permission(user, base):
            raise PermissionDenied
        plugin_admin = base.get_plugin_class()(instance.__class__, admin.site)
        form_class = plugin_admin.get_form(request_for(user), instance)
        initial = form_class(instance=instance).initial
        if set(values or {}) - set(form_class.base_fields):
            msg = "Unknown plugin fields."
            raise ValidationError(msg)
        data = form_data({**initial, **(values or {})}, form_class)
        form = clean_form(form_class(data=data, instance=instance))
        instance = form.save()
    else:
        msg = "Unsupported plugin operation."
        raise ValidationError(msg)
    audit(user, f"plugins.{action}", instance.pk)
    return plugin_info(instance, user)


@transaction.atomic
def versions(user, action, kind, content_id):
    content = version_content(kind, content_id)
    content_permission(user, content, "view" if action == "list" else "change")
    if action == "draft":
        result = draft_for(user, content)
        audit(user, "versions.draft", result.pk)
        return content_info(result)
    version = Version.objects.get_for_content(content)
    if action == "list":
        ids = version.versionable.for_content_grouping_values(content).values_list(
            "pk",
            flat=True,
        )
        return list(
            Version.objects.filter(
                content_type=ContentType.objects.get_for_model(content),
                object_id__in=ids,
            ).values("id", "object_id", "number", "state", "created", "created_by_id"),
        )
    if action not in {"publish", "unpublish", "archive", "discard"}:
        msg = "Unsupported version operation."
        raise ValidationError(msg)
    check = getattr(version, f"check_{action}", None)
    if check is None or not check.as_bool(user):
        raise PermissionDenied
    if action == "discard":
        pk = version.pk
        version.delete()
        audit(user, "versions.discard", pk)
        return {"deleted_version": pk}
    getattr(version, action)(user)
    audit(user, f"versions.{action}", version.pk)
    return {"version": version.pk, "state": version.state}


@transaction.atomic
def stories(user, action, content_id=None, values=None, language="en"):
    values = values or {}
    if "post_text" in values:
        values = {**values, "post_text": HTMLFormField().clean(values["post_text"])}
    if action == "list":
        permit(user, "djangocms_stories.view_post")
        return [
            content_info(item)
            for item in PostContent.admin_manager.latest_content().filter(
                language=language,
            )[:100]
        ]
    allowed = {"title", "slug", "subtitle", "abstract", "post_text", "meta_description"}
    if action == "create":
        permit(user, "djangocms_stories.add_post")
        post = Post.objects.create(
            author=user,
            app_config_id=values["app_config_id"],
            main_image_id=values.get("image_id"),
        )
        post.sites.add(settings.SITE_ID)
        content = PostContent.objects.with_user(user).create(
            post=post,
            language=language,
            **{k: v for k, v in values.items() if k in allowed},
        )
    else:
        original = PostContent.admin_manager.get(pk=content_id)
        content_permission(
            user,
            original,
            "view" if action == "get" else "delete" if action == "delete" else "change",
        )
        if action == "get":
            return content_info(original)
        if action == "metadata":
            post = original.post
            fields = {
                "image_id": "main_image",
                "app_config_id": "app_config",
                "author_id": "author",
                "date_published": "date_published",
                "date_published_end": "date_published_end",
            }
            if set(values) - {*fields, "category_ids", "tags"}:
                msg = "Unsupported article metadata fields."
                raise ValidationError(msg)
            for key, value in values.items():
                if key in fields:
                    field = Post._meta.get_field(fields[key])  # noqa: SLF001
                    setattr(post, field.attname, field.clean(value, post))
            post.full_clean()
            post.save()
            if "category_ids" in values:
                post.categories.set(values["category_ids"])
            if "tags" in values:
                post.tags.set(values["tags"])
            audit(user, "stories.metadata", post.pk)
            return content_info(original)
        if action == "delete":
            pk = original.post_id
            delete_versioned_grouper(user, original.post, PostContent)
            audit(user, "stories.delete", pk)
            return {"deleted_post": pk}
        if action == "translate":
            permit(user, "djangocms_stories.add_post")
            content = PostContent.objects.with_user(user).create(
                post=original.post,
                language=language,
                **{k: v for k, v in values.items() if k in allowed},
            )
        elif action == "update":
            if set(values) - allowed:
                msg = "Unsupported article content fields."
                raise ValidationError(msg)
            content = draft_for(user, original)
            for key, value in values.items():
                setattr(content, key, value)
            content.full_clean()
            content.save()
        else:
            msg = "Unsupported article operation."
            raise ValidationError(msg)
    audit(user, f"stories.{action}", content.pk)
    return content_info(content)
