import uuid

from django.conf import settings
from django.db import models


class Upload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    kind = models.CharField(
        max_length=10,
        choices=[("file", "File"), ("image", "Image")],
    )
    expected_size = models.PositiveBigIntegerField()
    received_size = models.PositiveBigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True)
    folder = models.ForeignKey(
        "filer.Folder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    tool = models.CharField(max_length=80)
    target = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.tool}: {self.target}"
