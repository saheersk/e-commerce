import json 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from shop.models import Product, ProductImage, Category, Wishlist, Cart
from main.functions import paginate_instances



def product_all(request):
    sort_by_price = request.GET.get('sort_by_price')
    category_param = request.GET.get('category')
    q = request.GET.get('q')

    products = Product.objects.filter(is_show=True, category__is_blocked=False, is_deleted=False)

    if category_param:
        products = products.filter(category__name=category_param)

    if sort_by_price == 'low-to-high':
        products = products.order_by('price')
    elif sort_by_price == 'high-to-low':
        products = products.order_by('-price')
    
    if q:
        products = products.filter(Q(title__icontains=q))

    instances = paginate_instances(request, products, per_page=3)
    categories = Category.objects.filter(is_blocked=False, is_deleted=False)
    print(request.session.get('cart_count'))
    context = {
        'title': 'Male Fashion | Products',
        'products': instances,
        'categories': categories,
        'active_menu_item': "shop",
    }
    
    return render(request, 'product/shop.html', context)

   
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_images = ProductImage.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    context = {
        'title': f'Male Fashion | {product.title}',
        'product': product,
        'product_images': product_images,
        'related_products': related_products
    }
    return render(request, 'product/shop-details.html', context)


@login_required(login_url="user/login/")
def product_wishlist(request):
    if request.user.is_authenticated:
        products = Wishlist.objects.filter(user=request.user, is_deleted=False)
        context = {
            'title': 'Male Fashion | Wishlist',
            'products': products
        }
        return render(request, 'product/shop-wishlist.html', context)
    else:
        return redirect('user:admin_login')
    

@login_required(login_url="user/login/")
def product_wishlist_add(request, pk):
    product = get_object_or_404(Product, id=pk)

    if Wishlist.objects.filter(product=product).exists():
        instance = Wishlist.objects.get(product=product)
        # if instance.is_deleted == False:
        #     response_data = {
        #         "wishlist" : True,
        #         "title" : "Already added",
        #         "text" : "Product in Wishlist",
        #         "type" : "success",
        #     }

        #     return HttpResponse(json.dumps(response_data), content_type="application/json")

        instance.is_deleted = False
        instance.save()
    else:
        Wishlist.objects.create(
            product=product,
            user=request.user
        )

    data = {
        "message" : "success"
    }

    return JsonResponse(data)


@login_required(login_url="user/login/")
def product_wishlist_remove(request, pk):
    product = get_object_or_404(Wishlist, id=pk)

    product.is_deleted = True
    product.save()

    wishlist_items = Wishlist.objects.filter(user=request.user, is_deleted=False)
    wishlist_count = wishlist_items.count()

    data = {
        "message": "success",
        "count": wishlist_count
    }

    return JsonResponse(data)

@login_required(login_url="user/login/")
def product_cart(request):
    products = Cart.objects.filter(user=request.user, is_deleted=False)

    total_amount = products.aggregate(
        total_amount=Sum(
            ExpressionWrapper(
                F('product__price') * F('qty'),
                output_field=DecimalField()
            )
        )
    )['total_amount'] or 0

    for item in products:
        item.total_price_of_product = item.product.price * item.qty
        item.save()
   
    context = {
        "title": "Male Fashion | Cart",
        "products" : products,
        'total_amount': total_amount

    }
    return render(request, 'product/shopping-cart.html', context)


@login_required(login_url="user/login/")
def product_cart_add(request, pk):
    product = get_object_or_404(Product, id=pk)
    if Cart.objects.filter(product=product).exists():
        instance = Cart.objects.get(product=product)
        instance.is_deleted = False
        instance.qty = 1
        instance.save()
    else:
        Cart.objects.create(
            product=product,
            user=request.user,
            total_price_of_product=product.price
        )
    
    cart_count = request.session.get('cart_count', 0)
    count = request.session['cart_count'] = cart_count + 1

    response_data = {
            "success" : True,
            "title" : "Added to Cart",
            "message" : "Product is in cart now",
            "status" : "success",
            "cart_count" : count
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required(login_url="user/login/")
def update_product_quantity(request, pk):
    product = get_object_or_404(Cart, id=pk)

    action = request.POST.get('action') 

    if action == 'increment':
        if product.product.stock_unit - product.qty > 0:
            if product.qty < 10:
                product.qty += 1
            else:
                data = {
                    "exceeded": True,
                    "title" : "Quantity limit exceeded",
                    "message" : "Only 10 quantity per order is allowed",
                    "status" : "warning",
                }

                return JsonResponse(data)
        else:
            data = {
                    "exceeded": True,
                    "title" : "Quantity Not there",
                    "message" : "Sorry this much qty is not there",
                    "status" : "warning",
                }

            return JsonResponse(data)
        
    elif action == 'decrement':
        if product.qty > 1:
            product.qty -= 1

    product.save()

    products = Cart.objects.filter(user=request.user, is_deleted=False)

    total_amount = products.aggregate(
        total_amount=Sum(
            ExpressionWrapper(
                F('product__price') * F('qty'),
                output_field=DecimalField()
            )
        )
    )['total_amount'] or 0
    
    data = {
        'exceeded': False,
        'message' : "success",
        'qty' : product.qty,
        'amount': product.product.price * product.qty,
        'total_amount' : total_amount
    }

    return JsonResponse(data)


@login_required(login_url="user/login/")
def product_cart_remove(request, pk):
    product = get_object_or_404(Cart, id=pk)

    product.is_deleted = True

    product.save()

    cart_count = request.session.get('cart_count', 0)
    if cart_count > 0:
        count = request.session['cart_count'] = cart_count - 1

    response_data = {
            "success" : True,
            "title" : "Successfully Changed",
            "text" : "Product Updated successfully",
            "type" : "warning",
            "cart_count" : count
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")

