"""Re-encrypt staff MFA secrets after copying a database between environments.

TOTP secrets and recovery-code seeds are encrypted with a key derived from
SECRET_KEY (see StaffMFAAdapter). A database restored from another environment
still carries the other SECRET_KEY's ciphertexts, so MFA login fails until they
are re-encrypted with this environment's key.

The old key is read from the MFA_OLD_SECRET_KEY environment variable so it never
appears in the process list or shell history.
"""

import os

from allauth.mfa.models import Authenticator
from cryptography.fernet import InvalidToken
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from space_game.control.security import StaffMFAAdapter

ENCRYPTED_FIELDS = {
    Authenticator.Type.TOTP: "secret",
    Authenticator.Type.RECOVERY_CODES: "seed",
}
PREFIX = "fernet:"


class Command(BaseCommand):
    help = "Re-encrypt MFA secrets from MFA_OLD_SECRET_KEY to the current SECRET_KEY."

    def handle(self, *args, **options):
        old_key = os.environ.get("MFA_OLD_SECRET_KEY", "")
        if not old_key:
            msg = "MFA_OLD_SECRET_KEY is not set."
            raise CommandError(msg)

        adapter = StaffMFAAdapter()
        current = adapter.cipher()
        old = adapter.cipher([old_key])
        converted = skipped = failed = 0

        with transaction.atomic():
            for auth in Authenticator.objects.select_for_update().filter(
                type__in=ENCRYPTED_FIELDS,
            ):
                field = ENCRYPTED_FIELDS[auth.type]
                value = auth.data.get(field)
                if not isinstance(value, str) or not value.startswith(PREFIX):
                    skipped += 1
                    continue
                token = value[len(PREFIX) :].encode()
                try:
                    current.decrypt(token)
                except InvalidToken:
                    pass
                else:
                    skipped += 1  # already readable with this environment's key
                    continue
                try:
                    plain = old.decrypt(token)
                except InvalidToken:
                    failed += 1
                    self.stderr.write(
                        f"Authenticator {auth.pk} ({auth.type}, user {auth.user_id}) "
                        "cannot be decrypted with either key.",
                    )
                    continue
                auth.data[field] = PREFIX + current.encrypt(plain).decode()
                auth.save(update_fields=["data"])
                converted += 1

        self.stdout.write(
            f"MFA secrets re-encrypted: {converted}, "
            f"unchanged: {skipped}, failed: {failed}",
        )
        if failed:
            msg = "Some MFA secrets could not be re-encrypted."
            raise CommandError(msg)
