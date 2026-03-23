import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="to_json")
def to_json(value):
    """Safely serialize a value to JSON for use in templates."""
    return mark_safe(json.dumps(value))
