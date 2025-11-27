from django import template

register = template.Library()

@register.filter
def percent_to_float(value):
    """Convert percentage string like '4.2%' to float 4.2"""
    try:
        if isinstance(value, str) and value.endswith("%"):
            return float(value.strip("%"))
        return float(value)
    except (ValueError, TypeError):
        return 0.0
