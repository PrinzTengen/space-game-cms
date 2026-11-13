"""Bind the Stories overview to its editable CMS page."""

from cms.models import PageContent
from django.utils.deprecation import MiddlewareMixin


class LogbookToolbarMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        match = request.resolver_match
        if (
            not match
            or match.url_name != "posts-latest"
            or not request.user.is_staff
            or not hasattr(request, "toolbar")
        ):
            return response

        toolbar = request.toolbar
        page = getattr(request, "current_page", None)
        if page and page.reverse_id == "stories" and toolbar.get_object() is None:
            # Stories sets an object on article pages, but not on its list view.
            # Versioning needs the page object to offer Edit / New Draft.
            content = PageContent.objects.filter(
                page=page,
                language=toolbar.request_language,
            ).first()
            if content:
                toolbar.set_object(content)
        return response
