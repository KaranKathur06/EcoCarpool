from django import template
register = template.Library()

@register.filter
def get_digit_range(value, arg):
    """Returns a range from value down to arg (inclusive, descending)."""
    try:
        value = int(value)
        arg = int(arg)
        if value > arg:
            return range(value, arg - 1, -1)
        else:
            return range(value, arg + 1)
    except Exception:
        return [] 