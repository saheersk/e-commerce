import json 
import io
import hmac
import hashlib
import binascii
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import ExpressionWrapper, F, DecimalField, Sum, Case, When, Value, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.conf import settings
from django.template.loader import get_template

import razorpay
from xhtml2pdf import pisa

from shop.models import Product, ProductImage, Category, Wishlist, Cart, OrderStatus, Order, Payment, PaymentMethod, ProductVariant, OrderItem, WalletHistory
from user.models import Address, Coupon, CustomUser, CouponUsage, Wallet
from main.functions import paginate_instances
from shop.utils import generate_invoice_to_send_email


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

    instances = paginate_instances(request, products, per_page=8)
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

    total_amount = Cart.objects.filter(user=request.user, is_deleted=False).aggregate(
    total_amount=Coalesce(
                Sum(
                    Case(
                        When(product__discount_amount__gt=0.00, then=ExpressionWrapper(F('product__discount_amount'), output_field=DecimalField())),
                        default=ExpressionWrapper(F('product__price'), output_field=DecimalField()),
                    ) * F('qty'),
                    output_field=DecimalField(),
                ),
                Value(0.00),
                output_field=DecimalField(),
            )
        )['total_amount']

    for item in products:
        if item.product.discount_amount > 0.00:
            item.total_price_of_product = item.product.discount_amount * item.qty
        else:
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
    if Cart.objects.filter(user=request.user, product=product).exists():
        instance = Cart.objects.get(user=request.user, product=product)
        instance.is_deleted = False
        instance.qty = int(qty)
        instance.size = size
        print(product.discount_amount,'amount')
        if product.discount_amount > 0.00:
            print('hello')
            instance.total_price_of_product = product.discount_amount * int(qty)
            print(instance.total_price_of_product, 'total')
        else:
            print('else')
            instance.total_price_of_product = product.price * int(qty)

        instance.save()
    else:
        if product.discount_amount > 0.00:
            price = product.discount_amount
        else:
            price = product.price

        Cart.objects.create(
            product=product,
            user=request.user,
            qty=qty,
            size=size,
            total_price_of_product=price
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

    amount = 0
    if product.product.discount_amount > 0.00:
        amount = product.total_price_of_product = product.product.discount_amount * product.qty
    else:
        amount = product.total_price_of_product = product.product.price * product.qty

    product.save()

    products = Cart.objects.filter(user=request.user, is_deleted=False)

    total_amount = products.aggregate(
    total_amount=Coalesce(
                Sum(
                    Case(
                        When(product__discount_amount__gt=0.00, then=ExpressionWrapper(F('product__discount_amount'), output_field=DecimalField())),
                        default=ExpressionWrapper(F('product__price'), output_field=DecimalField()),
                    ) * F('qty'),
                    output_field=DecimalField(),
                ),
                Value(0.00),
                output_field=DecimalField(),
            )
        )['total_amount']
    
    data = {
        'exceeded': False,
        'message' : "success",
        'qty' : product.qty,
        'amount': amount,
        'total_amount' : total_amount
    }

    return JsonResponse(data)




@login_required(login_url="user/login/")
def product_cart_remove(request, pk):
    product = get_object_or_404(Cart, id=pk)

    product.qty =1
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
    if not Address.objects.filter(user=request.user, is_default=True).exists():
        return redirect("user_profile:profile_address_add")
    else:
        user_addresses = Address.objects.filter(user=request.user, is_default=False)
        user_default_address = Address.objects.get(user=request.user, is_default=True)

        current_datetime = timezone.now()

        used_coupon_codes = CouponUsage.objects.filter(user=request.user).values_list('coupon__code', flat=True)
        valid_coupons = Coupon.objects.filter(
            active=True,
            valid_to__gte=current_datetime,
        ).exclude(code__in=used_coupon_codes)

        products = Cart.objects.filter(user=request.user, is_deleted=False)

        total_amount = products.aggregate(
                total_amount=Coalesce(
                            Sum(
                                Case(
                                    When(product__discount_amount__gt=0.00, then=ExpressionWrapper(F('product__discount_amount'), output_field=DecimalField())),
                                    default=ExpressionWrapper(F('product__price'), output_field=DecimalField()),
                                ) * F('qty'),
                                output_field=DecimalField(),
                            ),
                            Value(0.00),
                            output_field=DecimalField(),
                        )
                    )['total_amount']
    

        print(total_amount, 'amount')
        wallet = request.session.get('wallet')

        discount_amount = 0
        for item in products:
            print(item.total_price_of_product)
            discount_amount += item.total_price_of_product

        discount = False
        if discount_amount != total_amount:
            discount = True

        print(discount, discount_amount, total_amount, 'amount')

        context = {
            "wallet" : wallet,
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


#Discount
def product_discount(request):
    if request.method == 'POST':
        code = request.POST.get('coupon')

        coupon = get_object_or_404(Coupon, code=code)
        
        user = request.user
        products = Cart.objects.filter(user=user, is_deleted=False)

        # total_amount = sum(item.product.price * item.qty for item in products)
        total_amount = products.aggregate(
                total_amount=Coalesce(
                            Sum(
                                Case(
                                    When(product__discount_amount__gt=0.00, then=ExpressionWrapper(F('product__discount_amount'), output_field=DecimalField())),
                                    default=ExpressionWrapper(F('product__price'), output_field=DecimalField()),
                                ) * F('qty'),
                                output_field=DecimalField(),
                            ),
                            Value(0.00),
                            output_field=DecimalField(),
                        )
                    )['total_amount']

        if CouponUsage.objects.filter(Q(user=user) & Q(coupon=coupon)).exists():
            response_data = {
                "title": "Used for previous orders",
                "status": "error",
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")


        # if request.session.get('coupon'):
        #     coupon_code = request.session.get('coupon')
        #     if coupon_code == coupon.code:
        #         response_data = {
        #             "title": "Already used one coupon",
        #             "status": "warning",
        #         }
        #         return HttpResponse(json.dumps(response_data), content_type="application/json")

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

        total_discount_amount = 0.00
        if coupon.discount_type == 'amount':
            discount = coupon.amount_or_percent / 2

            for item in products:
                item.total_price_of_product -= discount
                item.save()
                total_discount_amount += float(item.total_price_of_product)
        else:
            total_discount_percentage = coupon.amount_or_percent / 2
            print(total_discount_percentage, 'per')
            for item in products:
                discount = item.total_price_of_product * (total_discount_percentage / 100)
                print(discount, 'dis')
                item.total_price_of_product -= discount
                item.save()
                total_discount_amount += float(item.total_price_of_product)

        # CouponUsage.objects.create(
        #         user=request.user,
        #         coupon=coupon,
        #     )

        # CouponUsage.objects.create(user=user, coupon=coupon)
        # request.session['coupon'] = coupon.code

        total_discount_amount = round(total_discount_amount, 2)

        response_data = {
            "title": "Discount applied",
            "status": "success",
            "total_amount": total_discount_amount,
        }

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        # Handle other HTTP methods or return an appropriate response
        pass


#Payment
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
        
        request.session['wallet'] = False

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
            
        generate_invoice_to_send_email(request, order.id)

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

        request.session['wallet'] = False

        products = Cart.objects.filter(user=user, is_deleted=False)
        shipping_address = Address.objects.get(user=user, id=address)
        order_status = OrderStatus.objects.get(status="Pending")
        payment_type = PaymentMethod.objects.get(payment_type="Online")

        total_amount = 0.00
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
                total_amount += float(item.total_price_of_product)


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

        generate_invoice_to_send_email(request, order.id)
        response_data = {
                    "status" : "success",
                    "title" : "Order Purchased",
                    "message" : "Your Product will be deliver shortly",
                }

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    

def product_order_wallet(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST.get('address')

        products = Cart.objects.filter(user=user, is_deleted=False)
        wallet = Wallet.objects.get(user=request.user)
        shipping_address = Address.objects.get(user=user, id=address)
        order_status = OrderStatus.objects.get(status="Pending")
        payment_type = PaymentMethod.objects.get(payment_type="Wallet")

        total_amount = Decimal(0.00)

        for item in products:
             total_amount += item.total_price_of_product


        order = Order.objects.create(
                        user=user,
                        shipping_address=shipping_address,
                    )
            
        if wallet.balance > total_amount:
            wallet.balance -= total_amount
            wallet.save()
            
            WalletHistory.objects.create(
                wallet=wallet,
                order=order,
                description="Amount for this order is debited.",
                amount=total_amount,
                transaction_operation='debit'
            )

            request.session['wallet'] = False

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
                    transaction_id='wallet',
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
            
            generate_invoice_to_send_email(request, order.id)
            response_data = {
                        "wallet": True,
                        "status" : "success",
                        "title" : "Order Purchased",
                        "message" : "Your Product will be deliver shortly",
                    }

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            total_amount = Decimal(0.00)
            for item in products:
                item.total_price_of_product -= wallet.balance // 2
                item.save()
                total_amount += item.total_price_of_product

            WalletHistory.objects.create(
                wallet=wallet,
                order=order,
                amount=total_amount,
                description="Amount for this order is debited.",
                transaction_operation='debit'
            )

            wallet.balance = 0
            request.session['wallet'] = True
            wallet.save()

            response_data = {
                        "wallet": False,
                        "status" : "success",
                        "title" : "Order Purchased",
                        "message" : "Your Product will be deliver shortly",
                        "total_amount" : total_amount
                    }

            return HttpResponse(json.dumps(response_data), content_type="application/json")


def create_payment(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        amount = float(request.POST.get('amount')) * 100  

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
    print(data)
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


#invoice
def generate_invoice_pdf(request, pk):
    order = get_object_or_404(Order, id=pk)
    invoice_id = hashlib.sha1(str(order.id).encode()).hexdigest()

    total_amount = 0
    for item in order.order_items.all():
        total_amount += item.quantity * item.product.price
         
    context = {'order': order, 'invoice_id': invoice_id, 'total_amount': total_amount}

    template_path = 'product/invoice-template.html' 
    template = get_template(template_path)
    context = {'order': order, 'invoice_id': invoice_id, 'total_amount': total_amount}  # Pass data to your template
    html = template.render(context)
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)

    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    return response     