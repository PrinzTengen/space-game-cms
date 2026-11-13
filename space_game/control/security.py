"""Staff sessions must prove an enrolled second factor before managing content."""

import base64
import hashlib

from allauth.account.authentication import get_authentication_records
from allauth.account.stages import EmailVerificationStage
from allauth.mfa.adapter import DefaultMFAAdapter
from allauth.mfa.models import Authenticator
from cryptography.fernet import Fernet
from cryptography.fernet import MultiFernet
from django.conf import settings


def staff_mfa_verified(request):
    user = request.user
    if not user.is_authenticated or not user.is_active or not user.is_staff:
        return False
    authenticators = dict(
        Authenticator.objects.filter(user=user).values_list("pk", "type"),
    )
    if Authenticator.Type.TOTP not in authenticators.values():
        return False
    return any(
        record.get("method") == "mfa"
        and authenticators.get(record.get("id")) == record.get("type")
        and record.get("type")
        in {Authenticator.Type.TOTP, Authenticator.Type.RECOVERY_CODES}
        for record in get_authentication_records(request, user)
    )


class StaffMFAAdapter(DefaultMFAAdapter):
    @staticmethod
    def cipher():
        keys = [settings.SECRET_KEY, *settings.SECRET_KEY_FALLBACKS]
        return MultiFernet(
            [
                Fernet(
                    base64.urlsafe_b64encode(
                        hashlib.sha256(
                            ("space-game-mfa-v1:" + key).encode(),
                        ).digest(),
                    ),
                )
                for key in keys
            ],
        )

    def encrypt(self, text):
        return "fernet:" + self.cipher().encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text):
        if encrypted_text.startswith("fernet:"):
            return self.cipher().decrypt(encrypted_text[7:].encode()).decode()
        return encrypted_text  # Existing allauth enrollments remain usable.

    def can_delete_authenticator(self, authenticator):
        if (
            authenticator.user.is_staff
            and authenticator.type == Authenticator.Type.TOTP
        ):
            return False
        return super().can_delete_authenticator(authenticator)


class StaffEmailVerificationStage(EmailVerificationStage):
    def handle(self):
        # Staff accounts are provisioned by an administrator. TOTP enrollment
        # must also work for createsuperuser accounts without verified email.
        if self.login.user and self.login.user.is_staff:
            return None, True
        return super().handle()
