from django import template

register = template.Library()

@register.filter
def should_break(value, should_break):
    """
    Custom template filter to set a variable to indicate whether to break a loop.
    """
    if should_break:
        value[0] = True
    return value