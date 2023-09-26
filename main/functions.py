from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def generate_form_error(form):
    message = ""
    for field in form:
        if field.errors:
            message +=  field.errors
    for err in form.non_field_errors():
        message += str(err)

    return message     


def paginate_instances(request, instance, per_page=3):
    instances = Paginator(instance, per_page)
    page = request.GET.get('page', 1)

    try:
        instances = instances.page(page)
    except PageNotAnInteger:
        instances = instances.page(1)
    except EmptyPage:
        instances = instances.page(instances.num_pages)
     
    return instances