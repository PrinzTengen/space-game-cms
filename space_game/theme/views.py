"""Language selection and public launcher downloads."""

from django.conf import settings
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.views.i18n import set_language

from space_game.theme.downloads import launcher_file
from space_game.theme.downloads import launcher_url
from space_game.theme.downloads import published_launcher_config


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
    config = published_launcher_config(platform, request.GET.get("language"))
    if config is None:
        raise Http404
    if config.get("launcher_file"):
        attached = launcher_file(config)
        if attached is None:
            raise Http404
        try:
            stream = attached.file.open("rb")
        except OSError as exc:
            raise Http404 from exc
        return FileResponse(
            stream,
            as_attachment=True,
            filename=attached.original_filename
            or attached.file.name.rsplit("/", 1)[-1],
            content_type="application/octet-stream",
        )
    destination = launcher_url(config)
    if not destination:
        raise Http404
    return HttpResponseRedirect(destination)
