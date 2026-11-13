# ruff: noqa: C901, PLR0912, PLR0913, PLR0915, PLR0917
import base64
import binascii
import hashlib
import mimetypes
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.files import File as DjangoFile
from django.db import transaction
from django.utils import timezone
from filer.models import File
from filer.models import Folder
from filer.models import Image
from filer.validation import validate_upload
from PIL import Image as PILImage

from space_game.control.cms_services import permit
from space_game.control.models import Upload
from space_game.control.services import audit
from space_game.control.services import request_for

MAX_FILENAME_LENGTH = 255
MAX_PENDING_UPLOADS = 5
MAX_BASE64_CHARS = 1400000


def upload_path(upload):
    root = Path(settings.MCP_UPLOAD_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root / str(upload.pk)


def media_info(obj):
    result = {
        "id": obj.pk,
        "name": obj.name,
        "filename": obj.original_filename,
        "description": obj.description,
        "size": obj.size,
        "folder_id": obj.folder_id,
        "is_public": obj.is_public,
        "url": obj.url if obj.is_public else None,
        "kind": "image" if isinstance(obj, Image) else "file",
    }
    if isinstance(obj, Image):
        result.update(
            default_alt_text=obj.default_alt_text,
            default_caption=obj.default_caption,
        )
    return result


@transaction.atomic
def media(user, action, file_id=None, values=None, folder_id=None, limit=50):
    request = request_for(user)
    if action == "list":
        if not (user.has_perm("filer.view_file") or user.has_perm("filer.view_image")):
            raise PermissionDenied
        queryset = File.objects.all().order_by("pk")
        if folder_id is not None:
            queryset = queryset.filter(folder_id=folder_id)
        return [
            media_info(item)
            for item in queryset[: min(max(limit, 1), 100)]
            if item.has_read_permission(request)
            and user.has_perm(
                "filer.view_image" if isinstance(item, Image) else "filer.view_file",
            )
        ]
    obj = File.objects.get(pk=file_id)
    operation = (
        "view" if action == "get" else "delete" if action == "delete" else "change"
    )
    permit(user, f"filer.{operation}_{'image' if isinstance(obj, Image) else 'file'}")
    if not (
        obj.has_read_permission(request)
        if action == "get"
        else obj.has_edit_permission(request)
    ):
        raise PermissionDenied
    if action == "get":
        return media_info(obj)
    if action == "delete":
        obj.delete()
        audit(user, "media.delete", file_id)
        return {"deleted": file_id}
    editable = {
        "name",
        "description",
        "folder_id",
        "original_filename",
    }
    if isinstance(obj, Image):
        editable |= {"default_alt_text", "default_caption"}
    if action != "update" or set(values or {}) - editable:
        msg = "Only file metadata can be edited; upload a new file for changed bytes."
        raise ValidationError(msg)
    for key, value in (values or {}).items():
        if key == "folder_id" and value is not None:
            folder = Folder.objects.get(pk=value)
            if not folder.has_add_children_permission(request):
                raise PermissionDenied
        setattr(obj, key, value)
    obj.full_clean()
    obj.save()
    audit(user, "media.update", file_id)
    return media_info(obj)


@transaction.atomic
def uploads(
    user,
    action,
    upload_id=None,
    filename=None,
    size=None,
    kind="file",
    chunk=None,
    offset=None,
    sha256="",
    folder_id=None,
):
    if action == "list":
        return {
            "uploads": list(
                Upload.objects.filter(owner=user).values(
                    "id",
                    "filename",
                    "kind",
                    "expected_size",
                    "received_size",
                    "created",
                ),
            ),
        }
    if action == "begin":
        if (
            kind not in {"file", "image"}
            or not isinstance(size, int)
            or not 0 < size <= settings.MCP_MAX_UPLOAD_BYTES
        ):
            msg = "Invalid upload kind or size."
            raise ValidationError(msg)
        permit(user, "filer.add_image" if kind == "image" else "filer.add_file")
        if (
            not filename
            or filename in {".", ".."}
            or filename != Path(filename).name
            or "\\" in filename
            or len(filename) > MAX_FILENAME_LENGTH
        ):
            msg = "Use a filename without directories."
            raise ValidationError(msg)
        if sha256 and not re.fullmatch(r"[0-9a-fA-F]{64}", sha256):
            msg = "Invalid SHA-256 checksum."
            raise ValidationError(msg)
        if Upload.objects.filter(owner=user).count() >= MAX_PENDING_UPLOADS:
            msg = "Finish or abort your pending uploads first."
            raise ValidationError(msg)
        if folder_id and not Folder.objects.get(
            pk=folder_id,
        ).has_add_children_permission(request_for(user)):
            raise PermissionDenied
        upload = Upload.objects.create(
            owner=user,
            filename=filename,
            kind=kind,
            expected_size=size,
            sha256=sha256.lower(),
            folder_id=folder_id,
        )
        upload_path(upload).touch(exist_ok=False)
        audit(user, "uploads.begin", upload.pk)
        return {
            "upload_id": str(upload.pk),
            "offset": 0,
            "max_chunk_bytes": 1024 * 1024,
        }
    upload = Upload.objects.select_for_update().get(pk=upload_id, owner=user)
    if action == "status":
        return {
            "upload_id": str(upload.pk),
            "offset": upload.received_size,
            "size": upload.expected_size,
        }
    if action != "abort" and upload.created < timezone.now() - timedelta(hours=24):
        msg = "Upload expired; abort it and start again."
        raise ValidationError(msg)
    path = upload_path(upload)
    if action == "abort":
        path.unlink(missing_ok=True)
        upload.delete()
        audit(user, "uploads.abort", upload_id)
        return {"aborted": str(upload_id)}
    permit(user, "filer.add_image" if upload.kind == "image" else "filer.add_file")
    if action == "chunk":
        if (
            offset != upload.received_size
            or not isinstance(chunk, str)
            or len(chunk) > MAX_BASE64_CHARS
        ):
            msg = "Invalid chunk size or offset."
            raise ValidationError(msg)
        try:
            data = base64.b64decode(chunk, validate=True)
        except (binascii.Error, ValueError) as exc:
            msg = "Invalid base64 chunk."
            raise ValidationError(msg) from exc
        if (
            not data
            or len(data) > 1024 * 1024
            or upload.received_size + len(data) > upload.expected_size
        ):
            msg = "Chunk exceeds the declared file size."
            raise ValidationError(msg)
        with path.open("r+b") as stream:
            stream.seek(upload.received_size)
            stream.truncate()
            stream.write(data)
        upload.received_size += len(data)
        upload.save(update_fields=["received_size"])
        return {"upload_id": str(upload.pk), "offset": upload.received_size}
    if action != "finish" or upload.received_size != upload.expected_size:
        msg = "Upload is incomplete."
        raise ValidationError(msg)
    if upload.kind == "image":
        permit(user, "filer.add_image")
        with PILImage.open(path) as image:
            image.verify()
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if upload.sha256 and digest != upload.sha256:
        msg = "Upload checksum does not match."
        raise ValidationError(msg)
    # Use exactly the site's native Filer upload validators/sanitizers.
    with path.open("r+b") as stream:
        validate_upload(
            upload.filename,
            stream,
            user,
            mimetypes.guess_type(upload.filename)[0] or "application/octet-stream",
        )
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    model = Image if upload.kind == "image" else File
    with path.open("rb") as stream:
        attached = model(
            file=DjangoFile(stream, name=upload.filename),
            original_filename=upload.filename,
            owner=user,
            folder=upload.folder,
            is_public=True,
        )
        attached.full_clean(
            exclude=[
                "file",
                "_file_size",
                "sha1",
                "has_all_mandatory_data",
                "mime_type",
            ],
        )
        attached.save()
    result = {
        **media_info(attached),
        "sha256": digest,
        "reference": {"model": attached._meta.label_lower, "pk": attached.pk},  # noqa: SLF001
    }
    path.unlink()
    upload.delete()
    audit(user, "uploads.finish", attached.pk)
    return result
