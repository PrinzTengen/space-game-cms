"""Design-system attributes for the native frontend Link / Button plugin."""

from django import template

register = template.Library()


@register.simple_tag
def button_attributes(instance):
    if instance.config.get("link_type") == "btn":
        instance.add_classes("btn")
        if instance.config.get("link_context") == "primary" and not instance.config.get(
            "link_outline",
        ):
            instance.add_classes("btn-galaxy")
    return instance.get_attributes()
