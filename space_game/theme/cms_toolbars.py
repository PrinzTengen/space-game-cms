"""Load the editor theme through the CMS toolbar's native asset pipeline."""

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class MissionControlToolbar(CMSToolbar):
    class Media:
        css = {"all": ("build/cms-editor.css",)}
        js = ("js/admin-theme.js",)
