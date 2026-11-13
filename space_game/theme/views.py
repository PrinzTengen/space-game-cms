"""Language selection and public launcher downloads."""

from django.conf import settings
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.views.i18n import set_language

from space_game.theme.downloads import published_launcher_url


@require_POST
def switch_language(request):
    response = set_language(request)
    cookie = response.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie:
        # CMS refreshes its language cookie from the active translation afterward.
        translation.activate(cookie.value)
    return response


@require_GET
def launcher_download(request, platform):
    destination = published_launcher_url(platform, request.GET.get("language"))
    if not destination:
        raise Http404
    return HttpResponseRedirect(destination)
