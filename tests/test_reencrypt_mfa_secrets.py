import pytest
from allauth.mfa.models import Authenticator
from django.core.management import call_command
from django.core.management.base import CommandError

from space_game.control.security import StaffMFAAdapter
from space_game.users.models import User

OLD_KEY = "old-environment-secret-key"


def _encrypt(keys, text):
    return "fernet:" + StaffMFAAdapter.cipher(keys).encrypt(text.encode()).decode()


@pytest.mark.django_db
def test_reencrypts_secrets_from_old_key(monkeypatch):
    user = User.objects.create(username="staff", is_staff=True)
    totp = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.TOTP,
        data={"secret": _encrypt([OLD_KEY], "JBSWY3DPEHPK3PXP")},
    )
    codes = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.RECOVERY_CODES,
        data={"seed": _encrypt([OLD_KEY], "abc123"), "used_mask": 0},
    )
    monkeypatch.setenv("MFA_OLD_SECRET_KEY", OLD_KEY)

    call_command("reencrypt_mfa_secrets")
    # Running twice is harmless.
    call_command("reencrypt_mfa_secrets")

    adapter = StaffMFAAdapter()
    totp.refresh_from_db()
    codes.refresh_from_db()
    assert adapter.decrypt(totp.data["secret"]) == "JBSWY3DPEHPK3PXP"
    assert adapter.decrypt(codes.data["seed"]) == "abc123"
    assert codes.data["used_mask"] == 0


@pytest.mark.django_db
def test_fails_for_unknown_key(monkeypatch):
    user = User.objects.create(username="staff", is_staff=True)
    Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.TOTP,
        data={"secret": _encrypt(["some-other-key"], "JBSWY3DPEHPK3PXP")},
    )
    monkeypatch.setenv("MFA_OLD_SECRET_KEY", OLD_KEY)

    with pytest.raises(CommandError):
        call_command("reencrypt_mfa_secrets")
