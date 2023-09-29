import re

from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.simple_tag
def get_elided_page_range(instances, number, on_each_side=3, on_ends=2):
    paginator = Paginator(instances.object_list, instances.per_page)
    return paginator.get_elided_page_range(number=number, on_each_side=on_each_side, on_ends=on_ends)


@register.simple_tag(takes_context=True)
def change_params(context, page):
    request = context['request']
    full_path = request.get_full_path()

    if "?" in full_path:
        if "page" in full_path:
            full_path = re.sub("page=[0-9]+", f"page={page}", full_path)
        else:
            full_path += f"&page={page}"
    else:
        full_path += f"?page={page}"

    return full_path


@register.inclusion_tag("web/includes/pagination.html", takes_context=True)
def load_pagination(context, instances):
    request = context['request']
    return {
        "instances": instances,
        "request": request
    }