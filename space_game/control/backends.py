from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AdminAuthenticationBackend(ModelBackend):
    """Only active Django staff accounts may authenticate or retain a session.

    Usernames are matched case-insensitively, like allauth's login form did
    before, so ``createsuperuser`` accounts work regardless of typed casing.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)
        if username is None or password is None:
            return None
        field = f"{user_model.USERNAME_FIELD}__iexact"
        # _default_manager is Django's documented way to reach a swappable model.
        manager = user_model._default_manager  # noqa: SLF001
        users = list(manager.filter(**{field: username})[:2])
        if len(users) != 1:
            # Unknown or ambiguous username: still hash once against timing probes.
            user_model().set_password(password)
            return None
        user = users[0]
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_staff
