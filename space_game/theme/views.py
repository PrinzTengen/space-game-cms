"""Launcher downloads use server-side Discord authentication, never demo state."""

from urllib.parse import urlsplit

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.views.i18n import set_language


@require_POST
def switch_language(request):
    response = set_language(request)
    cookie = response.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie:
        # CMS refreshes its language cookie from the active translation afterward.
        translation.activate(cookie.value)
    return response


@login_required
@require_GET
def launcher_download(request, platform):
    if not SocialAccount.objects.filter(user=request.user, provider="discord").exists():
        raise PermissionDenied
    destination = settings.SG_LAUNCHER_URLS.get(platform)
    if not destination or urlsplit(destination).scheme != "https":
        raise Http404
    return HttpResponseRedirect(destination)
