from django.contrib import admin

from space_game.control.models import AuditEvent
from space_game.control.models import Upload


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["created", "actor", "tool", "target"]
    readonly_fields = ["created", "actor", "tool", "target"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ["filename", "owner", "received_size", "expected_size", "created"]
    readonly_fields = [
        "owner",
        "filename",
        "kind",
        "received_size",
        "expected_size",
        "sha256",
        "folder",
        "created",
    ]

    def has_add_permission(self, request):
        return False
