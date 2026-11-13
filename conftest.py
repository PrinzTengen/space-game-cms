# ruff: noqa: PLC0415
"""Keep force_login's fully authenticated semantics for existing CMS tests.

Security tests marked real_mfa exercise the actual password/enrollment/challenge
flow and deliberately do not receive this test-client authentication shortcut.
"""

import pytest


@pytest.fixture(autouse=True)
def complete_staff_force_login(request, monkeypatch):
    if request.node.get_closest_marker("real_mfa"):
        return
    from allauth.account.internal.flows.login import record_authentication
    from allauth.mfa.models import Authenticator
    from allauth.mfa.totp.internal.auth import TOTP
    from allauth.mfa.totp.internal.auth import generate_totp_secret
    from django.test import Client
    from django.test import RequestFactory

    original = Client.force_login

    def fully_authenticated(client, user, backend=None):
        original(client, user, backend=backend)
        if user.is_staff:
            authenticator = Authenticator.objects.filter(user=user, type="totp").first()
            if authenticator is None:
                authenticator = TOTP.activate(user, generate_totp_secret()).instance
            session = client.session
            fake = RequestFactory().get("/")
            fake.user = user
            fake.session = session
            record_authentication(fake, user, "mfa", id=authenticator.pk, type="totp")
            session.save()

    monkeypatch.setattr(Client, "force_login", fully_authenticated)
