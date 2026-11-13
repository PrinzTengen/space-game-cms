from pathlib import Path

from allauth.account.internal.flows.login import record_authentication
from allauth.mfa.models import Authenticator
from allauth.mfa.signals import authenticator_added
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from oauth2_provider.models import AccessToken
from oauth2_provider.models import RefreshToken

from space_game.control.models import Upload


@receiver(authenticator_added, dispatch_uid="staff_totp_enrollment_proof")
def enrollment_verified(sender, request, user, authenticator, **kwargs):
    # This signal follows successful code validation in allauth's enrollment view.
    if user.is_staff and authenticator.type == Authenticator.Type.TOTP:
        record_authentication(
            request,
            user,
            "mfa",
            id=authenticator.pk,
            type=authenticator.type,
        )


def revoke_management_tokens(user_id):
    RefreshToken.objects.filter(user_id=user_id).delete()
    AccessToken.objects.filter(user_id=user_id).delete()


@receiver(post_delete, sender=Authenticator)
def revoke_after_factor_reset(sender, instance, **kwargs):
    if instance.type == Authenticator.Type.TOTP:
        revoke_management_tokens(instance.user_id)


@receiver(pre_save, sender=get_user_model())
def remember_credential_change(sender, instance, **kwargs):
    previous = (
        sender.objects.filter(pk=instance.pk)
        .values("password", "is_active", "is_staff")
        .first()
        if instance.pk
        else None
    )
    instance.control_revoke_tokens = bool(
        previous and any(previous[key] != getattr(instance, key) for key in previous),
    )


@receiver(post_save, sender=get_user_model())
def revoke_after_credential_change(sender, instance, **kwargs):
    if getattr(instance, "control_revoke_tokens", False):
        revoke_management_tokens(instance.pk)


@receiver(post_delete, sender=Upload)
def remove_upload_bytes(sender, instance, **kwargs):
    (Path(settings.MCP_UPLOAD_ROOT) / str(instance.pk)).unlink(missing_ok=True)
