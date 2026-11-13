# ruff: noqa: C901, PLR0912, PLR0913, PLR0917
"""Permission-checked management primitives shared by the MCP tools and tests."""

import json

from cms.models import CMSPlugin
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models import QuerySet
from django.http import QueryDict
from django.test.client import RequestFactory
from django.utils.html import strip_tags

from space_game.control.models import AuditEvent

BLOCKED_APPS = {
    "account",
    "socialaccount",
    "mfa",
    "sessions",
    "authtoken",
    "oauth2_provider",
    "contenttypes",
    "admin",
    "control",
    "cms",
    "djangocms_versioning",
    "filer",
}
SECRET_FIELDS = {"password", "secret", "token", "key", "data", "client_secret", "sha1"}


def actor(token, scope="mcp:read"):
    if token is None or scope not in token.scopes:
        msg = "Missing management scope."
        raise PermissionDenied(msg)
    user = get_user_model().objects.get(pk=token.subject)
    if not user.is_active or not user.is_staff:
        raise PermissionDenied
    return user


def request_for(user):
    request = RequestFactory().get("/mcp")
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)  # noqa: SLF001
    return request


def audit(user, tool, target):
    AuditEvent.objects.create(actor=user, tool=tool, target=str(target)[:255])


def plain(value):
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


def schema(form):
    result = {}
    for name, field in form.base_fields.items():
        result[name] = {
            "label": str(field.label or name),
            "required": field.required,
            "type": field.__class__.__name__,
            "help": strip_tags(str(field.help_text)),
            "write_only": isinstance(field.widget, forms.PasswordInput),
        }
        if isinstance(field, forms.ChoiceField) and not isinstance(
            field,
            forms.ModelChoiceField,
        ):
            result[name]["choices"] = [
                (str(key), str(label)) for key, label in list(field.choices)[:100]
            ]
    return result


def form_data(values, form_class=None):
    data = QueryDict(mutable=True)
    for name, raw_value in values.items():
        value = raw_value
        field = form_class.base_fields.get(name) if form_class else None
        if field and isinstance(field.widget, forms.MultiWidget):
            parts = field.prepare_value(value)
            if not isinstance(parts, (list, tuple)):
                parts = field.widget.decompress(parts)
            for index, part in enumerate(parts):
                data[f"{name}_{index}"] = "" if part is None else str(part)
            continue
        if isinstance(value, Model):
            value = value.pk
        if isinstance(value, QuerySet):
            value = list(value.values_list("pk", flat=True))
        if isinstance(value, dict) and set(value) == {"model", "pk"}:
            value = value["pk"]
        if isinstance(value, list):
            data.setlist(name, [str(item) for item in value])
        elif isinstance(value, dict):
            data[name] = json.dumps(value)
        elif isinstance(value, bool):
            data[name] = "on" if value else ""
        elif value is not None:
            data[name] = str(value)
    return data


def clean_form(form):
    if not form.is_valid():
        raise ValidationError(form.errors.as_json())
    return form


def serialize(obj):
    fields = {}
    for field in obj._meta.concrete_fields:  # noqa: SLF001
        if field.name in SECRET_FIELDS or not field.editable:
            continue
        value = getattr(obj, field.attname)
        fields[field.name] = plain(value)
    for field in obj._meta.many_to_many:  # noqa: SLF001
        fields[field.name] = list(getattr(obj, field.name).values_list("pk", flat=True))
    return {"id": obj.pk, "label": str(obj), "fields": fields}


def model_admin(label):
    for model, modeladmin in admin.site._registry.items():  # noqa: SLF001
        if model._meta.label_lower == label.lower():  # noqa: SLF001
            if (
                (
                    model._meta.app_label in BLOCKED_APPS  # noqa: SLF001
                    and label.lower() != "filer.folder"
                )
                or issubclass(model, CMSPlugin)
                or label.lower()
                in {"djangocms_stories.post", "djangocms_stories.postcontent"}
            ):
                break
            return model, modeladmin
    msg = "Use the dedicated CMS, Stories, media or version tools for this model."
    raise PermissionDenied(msg)


def catalog(user):
    request = request_for(user)
    result = []
    for model, modeladmin in admin.site._registry.items():  # noqa: SLF001
        label = model._meta.label_lower  # noqa: SLF001
        try:
            model_admin(label)
        except PermissionDenied:
            continue
        if any(modeladmin.get_model_perms(request).values()):
            result.append(
                {
                    "model": label,
                    "name": str(model._meta.verbose_name_plural),  # noqa: SLF001
                    "add": modeladmin.has_add_permission(request),
                    "change": modeladmin.has_change_permission(request),
                    "delete": modeladmin.has_delete_permission(request),
                },
            )
    return result


def records(
    user,
    action,
    model,
    object_id=None,
    values=None,
    search="",
    limit=50,
    offset=0,
):
    model_class, modeladmin = model_admin(model)
    request = request_for(user)
    queryset = modeladmin.get_queryset(request)
    obj = queryset.get(pk=object_id) if object_id is not None else None
    if (
        model_class is get_user_model()
        and action not in {"list", "get", "schema"}
        and not user.is_superuser
    ):
        msg = "User management requires a superuser."
        raise PermissionDenied(msg)
    if action in {"list", "get", "schema"}:
        if not modeladmin.has_view_permission(request, obj):
            raise PermissionDenied
        if action == "schema":
            return schema(modeladmin.get_form(request, obj, change=obj is not None))
        if action == "get":
            return serialize(obj)
        queryset, _ = modeladmin.get_search_results(request, queryset, search)
        return {
            "count": queryset.count(),
            "results": [
                serialize(item)
                for item in queryset.order_by("pk")[
                    max(0, offset) : max(0, offset) + min(max(limit, 1), 100)
                ]
            ],
        }
    if action == "delete":
        if obj is None or not modeladmin.has_delete_permission(request, obj):
            raise PermissionDenied
        _, _, required, protected = modeladmin.get_deleted_objects([obj], request)
        if required or protected:
            msg = "Related objects prevent deletion."
            raise PermissionDenied(msg)
        target = f"{model}:{obj.pk}"
        modeladmin.log_deletions(request, [obj])
        modeladmin.delete_model(request, obj)
        audit(user, "records.delete", target)
        return {"deleted": target}
    if action not in {"create", "update"}:
        msg = "Unsupported operation."
        raise ValidationError(msg)
    if action == "create" and not modeladmin.has_add_permission(request):
        raise PermissionDenied
    if action == "update" and (
        obj is None or not modeladmin.has_change_permission(request, obj)
    ):
        raise PermissionDenied
    values = values or {}
    form_class = modeladmin.get_form(request, obj, change=obj is not None)
    # Preserve fields omitted by a partial edit, including many-to-many choices.
    initial = form_class(instance=obj).initial if obj is not None else {}
    data = {**initial, **values}
    for name in values:
        if name not in form_class.base_fields:
            msg = f"Field is not editable: {name}"
            raise ValidationError(msg)
    form = clean_form(form_class(data=form_data(data, form_class), instance=obj))
    saved = modeladmin.save_form(request, form, change=obj is not None)
    modeladmin.save_model(request, saved, form, change=obj is not None)
    modeladmin.save_related(request, form, [], change=obj is not None)
    if obj is None:
        modeladmin.log_addition(request, saved, "Created via MCP")
    else:
        modeladmin.log_change(request, saved, "Updated via MCP")
    audit(user, f"records.{action}", f"{model}:{saved.pk}")
    return serialize(saved)
