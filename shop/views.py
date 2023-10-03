import json 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.conf import settings

import razorpay
import hmac
import hashlib
import binascii

from shop.models import Product, ProductImage, Category, Wishlist, Cart, OrderStatus, Order, Payment, PaymentMethod, ProductVariant, OrderItem
from user.models import Address, Coupon, CustomUser, CouponUsage
from main.functions import paginate_instances



def product_all(request):
    sort_by_price = request.GET.get('sort_by_price')
    category_params = request.GET.getlist('category')  # Get a list of selected categories
    q = request.GET.get('q')

    products = Product.objects.filter(is_show=True, category__is_blocked=False, is_deleted=False)

    print(request.GET.getlist('category')  , 'cat')
    if 'shirt' in category_params:
        print('yes')

    if category_params and 'All' not in category_params:
        products = products.filter(category__name__in=category_params)

    if sort_by_price == 'low-to-high':
        products = products.order_by('price')
    elif sort_by_price == 'high-to-low':
        products = products.order_by('-price')
    
    if q:
        products = products.filter(Q(title__icontains=q))

    instances = paginate_instances(request, products, per_page=6)
    categories = Category.objects.filter(is_blocked=False, is_deleted=False)

    context = {
        'title': 'Male Fashion | Products',
        'products': instances,
        'categories': categories,
        'active_menu_item': "shop",
        'category_params': category_params
    }
    
    return render(request, 'product/shop.html', context)


   
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_images = ProductImage.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    variants = ProductVariant.objects.filter(product=product)


    context = {
        'title': f'Male Fashion | {product.title}',
        'product': product,
        'product_images': product_images,
        'variants': variants,
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

    request.session['cart_count'] = Cart.objects.filter(user=request.user, is_deleted=False).count() if request.user.is_authenticated else 0

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
    size = request.POST.get('size')
    qty = request.POST.get('quantity')
    print(size, qty, 'qty')
    if Cart.objects.filter(product=product).exists():
        instance = Cart.objects.get(product=product)
        instance.is_deleted = False
        instance.qty = int(qty)
        instance.size = size
        instance.total_price_of_product =  instance.product.price * instance.qty
        instance.save()
    else:
        Cart.objects.create(
            product=product,
            user=request.user,
            size=size,
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

    variant = ProductVariant.objects.get(product=product.product, size=product.size)

    action = request.POST.get('action') 
    print(action, 'action')
    if action == 'increment':
        if variant.stock_unit - product.qty > 0:
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
    
    product.total_price_of_product = product.product.price * product.qty

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
            "status" : "success",
            "title" : "Successfully Removed",
            "message" : "Product has been Successfully removed.",
            "cart_count" : count
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


#checkout
@login_required(login_url="user/login/")
def product_checkout(request):
    user_addresses = Address.objects.filter(user=request.user, is_default=False)
    user_default_address = Address.objects.get(user=request.user, is_default=True)

    current_datetime = timezone.now()

    valid_coupons = Coupon.objects.filter(active=True, valid_to__gte=current_datetime)
    products = Cart.objects.filter(user=request.user, is_deleted=False)

    total_amount = products.aggregate(
        total_amount=Sum(
            ExpressionWrapper(
                F('product__price') * F('qty'),
                output_field=DecimalField()
            )
        )
    )['total_amount'] or 0

    print(total_amount, 'amount')

    discount_amount = 0
    for item in products:
        print(item.total_price_of_product)
        discount_amount += item.total_price_of_product

    discount = False
    if discount_amount != total_amount:
        discount = True

    print(discount, discount_amount, total_amount, 'amount')

    context = {
        "title" : "Male Fashion | Product Checkout",
        "user_addresses": user_addresses,
        "user_default_address": user_default_address,
        "products": products,
        "coupons": valid_coupons,
        "total_amount": total_amount,
        "discount_amount": discount_amount,
        "discount" : discount
    }
    return render(request, 'product/checkout.html', context)


def product_discount(request):
    if request.method == 'POST':
        code = request.POST.get('coupon')

        coupon = get_object_or_404(Coupon, code=code)
        
        user = request.user
        products = Cart.objects.filter(user=user, is_deleted=False)

        total_amount = sum(item.product.price * item.qty for item in products)

        if request.session.get('coupon'):
            response_data = {
                "error": True,
                "title": "Already used one coupon",
                "status": "warning",
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        current_datetime = timezone.now()

        if current_datetime > coupon.valid_to:
            response_data = {
                "title": "Coupon not available",
                "status": "error",
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if total_amount <= coupon.min_purchase_amount:
            response_data = {
                "title": f"Minimum amount for this coupon is {coupon.min_purchase_amount}",
                "status": "error",
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        discount_amount = 0
        if coupon.discount_type == 'amount':
            discount = coupon.amount_or_percent / 2
            for item in products:
                item.total_price_of_product -= discount
                discount_amount += item.total_price_of_product 
                item.save()
        else:
            for item in products:
                item.total_price_of_product = item.total_price_of_product - (item.total_price_of_product * (coupon.amount_or_percent / 200))
                discount_amount += item.total_price_of_product 
                item.save()

        # CouponUsage.objects.create(user=user, coupon=coupon)
        request.session['coupon'] = coupon.code

        response_data = {
            "error": False,
            "title": "Discount applied",
            "status": "success",
            "total_amount": float(discount_amount),
        }

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        # Handle other HTTP methods or return an appropriate response
        pass



def product_order_cod(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST.get('address')

        products = Cart.objects.filter(user=user, is_deleted=False)
        shipping_address = Address.objects.get(user=user, id=address)
        order_status = OrderStatus.objects.get(status="Pending")
        payment_type = PaymentMethod.objects.get(payment_type="COD")

        total_amount = 0
        order = Order.objects.create(
                        user=user,
                        shipping_address=shipping_address,
                    )
            
        for item in products:
                order_item = OrderItem.objects.create(
                        product=item.product,
                        quantity=item.qty,
                        order_status=order_status,
                        size=item.size,
                        total_product_price=item.product.price * item.qty
                    )
                order.order_items.add(order_item)
                total_amount += item.total_price_of_product


        order.total_price = total_amount

        order.save()

        Payment.objects.create(
                order=order,
                user=user,
                payment_method=payment_type,
                transaction_id="COD",
                purchased_price=total_amount
            )
                
        for item in products:
                product = ProductVariant.objects.get(product=item.product, size=item.size)
                product.stock_unit -= item.qty
                product.save()
                item.is_deleted = True
                item.qty = 1
                item.total_price_of_product = item.product.price * item.qty
                item.save()
            
        if 'coupon' in request.session:
                del request.session['coupon']
            
        response_data = {
                    "status" : "success",
                    "title" : "Order Purchased",
                    "message" : "Your Product will be deliver shortly",
                }

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def product_order_digital(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST.get('address')
        payment_id = request.POST.get('payment_id')

        print(payment_id, 'payment_id')

        products = Cart.objects.filter(user=user, is_deleted=False)
        shipping_address = Address.objects.get(user=user, id=address)
        order_status = OrderStatus.objects.get(status="Pending")
        payment_type = PaymentMethod.objects.get(payment_type="COD")

        total_amount = 0
        order = Order.objects.create(
                        user=user,
                        shipping_address=shipping_address,
                    )
            
        for item in products:
                order_item = OrderItem.objects.create(
                        product=item.product,
                        quantity=item.qty,
                        order_status=order_status,
                        size=item.size,
                        total_product_price=item.product.price * item.qty
                    )
                order.order_items.add(order_item)
                total_amount += item.total_price_of_product


        order.total_price = total_amount

        order.save()

        Payment.objects.create(
                order=order,
                user=user,
                payment_method=payment_type,
                transaction_id=payment_id,
                purchased_price=total_amount
            )
                
        for item in products:
                product = ProductVariant.objects.get(product=item.product, size=item.size)
                product.stock_unit -= item.qty
                product.save()
                item.is_deleted = True
                item.qty = 1
                item.total_price_of_product = item.product.price * item.qty
                item.save()
            
        if 'coupon' in request.session:
                del request.session['coupon']
            
        response_data = {
                    "status" : "success",
                    "title" : "Order Purchased",
                    "message" : "Your Product will be deliver shortly",
                }

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    

def product_order_wallet(request):
    pass


def create_payment(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        amount = int(request.POST.get('amount')) * 100  

        order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        print(order['id'], 'id', settings.RAZORPAY_KEY_ID)    
        response_data = {
            'razorpayKey': str(settings.RAZORPAY_KEY_ID),
            'currency': order['currency'],
            'order_id': order['id'],
            'amount': order['amount']
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def payment_verify(request):
    data = request.POST
    razorpay_payment_id = data.getlist('payment_details[razorpay_payment_id]')[0]
    razorpay_order_id = data.getlist('payment_details[razorpay_order_id]')[0]
    razorpay_signature = data.getlist('payment_details[razorpay_signature]')[0]

    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    hashed = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), message.encode(), hashlib.sha256)
    generated_signature = binascii.hexlify(hashed.digest()).decode()

    if generated_signature == razorpay_signature:
        response_data = {
            'status': 'success',
            'message': 'Payment successful',
            'order_id': razorpay_order_id,
            'payment_id': razorpay_payment_id,
        }
        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})

