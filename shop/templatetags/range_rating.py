from django import template

register = template.Library()

@register.filter
def create_range(value):
    return range(value)