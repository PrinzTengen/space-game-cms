"""Brand the existing admin site, preserving all registered CMS integrations."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

admin.site.site_header = "Space Game"
admin.site.site_title = "Mission Control"
admin.site.index_title = _("Workspace")
