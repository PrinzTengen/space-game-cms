"""``static_alias`` that never leaves the page without its fallback."""

from django import template
from djangocms_alias.templatetags.djangocms_alias_tags import StaticAlias

register = template.Library()


class StaticAliasWithFallback(StaticAlias):
    """
    Same as djangocms-alias' ``{% static_alias "code" or %}…{% endstatic_alias %}``.

    The original only renders the ``or`` block for a published but empty alias.
    Anonymous visitors get nothing while the alias is not created or published
    for their language yet; this tag shows the fallback in that case as well.
    Subclassing keeps the declaration detectable for the CMS structure board.
    """

    # classytags would otherwise derive "static_alias_with_fallback".
    name = "static_alias"

    def render_tag(self, context, static_code, extra_bits, nodelist=None):
        content = super().render_tag(context, static_code, extra_bits, nodelist)
        if not content.strip() and nodelist:
            return nodelist.render(context)
        return content


register.tag(StaticAliasWithFallback.name, StaticAliasWithFallback)
