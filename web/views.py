import json

from django.shortcuts import render
from django.http import HttpResponse

from web.models import Banner, Showcase, FashionTrends
from web.forms import ContactForm
from shop.models import Product, Cart
from user.functions import generate_form_error


def index(request):
    banner = Banner.objects.filter(is_featured=True)
    showcase = Showcase.objects.filter(is_featured=True)[:3]
    trends = FashionTrends.objects.filter(is_featured=True)[:3]
    products = Product.objects.all()[:8]

    request.session['cart_count'] = Cart.objects.filter(user=request.user, is_deleted=False).count() if request.user.is_authenticated else 0

    context = {
        "title": "Male Fashion | Home",
        "banner": banner,
        "showcase": showcase, 
        "showcase_class": ['', 'banner__item--middle', 'banner__item--last'],
        "trends": trends,
        "products": products, 
        'active_menu_item': "home"
    }
    return render(request, 'web/index.html', context)


def about(request):
    context = {
        "title": "Male Fashion | About",
        'active_menu_item': "pages"
    }
    return render(request, 'web/about.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()

            response_data ={
                "title" : "Successfully Registered",
                "message" : "Will we contact you shortly",
                "status" : "success",
                "redirect" : "yes",
                "redirect_url" : "/"
            }
        
        else:
            error_message = generate_form_error(form)
            response_data = {
                "title" : "From validation error",
                "message" : str(error_message),
                "status" : "error",
                "stable" : "yes",
                }
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        context = {
            "title": "Male Fashion | Contact",
            'active_menu_item': "contact"
        }
        return render(request, 'web/contact.html', context)
