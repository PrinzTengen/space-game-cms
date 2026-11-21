"""Language selection and public launcher downloads."""

from urllib.parse import unquote
from urllib.parse import urlsplit

from django.conf import settings
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import NoReverseMatch
from django.urls import Resolver404
from django.urls import resolve
from django.urls import reverse
from django.utils import translation
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.views.i18n import set_language

from space_game.theme.design import published_posts
from space_game.theme.downloads import launcher_file
from space_game.theme.downloads import launcher_url
from space_game.theme.downloads import published_launcher_config


def _translated_story_url(url, target_language):
    parts = urlsplit(url)
    try:
        match = resolve(unquote(parts.path))
    except Resolver404:
        return url
    if match.app_name != "djangocms_stories" or match.url_name != "post-detail":
        return url

    post_id = (
        published_posts(translation.get_language())
        .filter(post__app_config__namespace=match.namespace, slug=match.kwargs["slug"])
        .values_list("post_id", flat=True)
        .first()
    )
    if post_id is None:
        return url

    content = published_posts(target_language).filter(post_id=post_id).first()
    translated_path = (
        content.get_absolute_url(language=target_language) if content else ""
    )
    if translated_path:
        return parts._replace(path=translated_path).geturl()
    try:
        with translation.override(target_language):
            return reverse(f"{match.namespace}:posts-latest")
    except NoReverseMatch:
        return "/"


@require_POST
def switch_language(request):
    response = set_language(request)
    cookie = response.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie:
        location = response.get("Location")
        if location and cookie.value != translation.get_language():
            response["Location"] = _translated_story_url(location, cookie.value)
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
