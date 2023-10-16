import json
import csv
from datetime import datetime

from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, \
      logout as auth_logout
from django.db.models import Q, Sum, Count
from django.forms import formset_factory
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder

from customadmin.forms import AdminCustomUserForm, AdminCustomUpdateUserForm, AdminCategory, AdminProduct, AdminProductImage, AdminOrderItemForm, AdminProductVariantFrom, AdminBannerForm, AdminCouponForm, AdminCategoryOfferForm, AdminProductOfferForm, AdminReviewForm, AdminReferralAmountForm, AdminBroadcastNotificationForm
from user.models import CustomUser, Wallet, Coupon, ReferralAmount
from web.models import Contact, Banner
from user.functions import generate_form_error
from shop.models import Category, Product, ProductImage, Order, ProductVariant, OrderItem, OrderManagement, OrderStatus, WalletHistory, Payment, CategoryOffer, ProductOffer, UserReview
from main.functions import paginate_instances
from customadmin.utils import send_user_refund_mail
from fashion_asgi.models import BroadcastNotification


class DateTimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


# Admin User
@login_required(login_url="admin-login/")
def admin_panel(request):
    if request.user.is_superuser and request.user.is_authenticated:
        total_revenue = Order.objects.filter(order_items__order_status__status="Delivered").aggregate(
            total_revenue=Sum('total_price')
        )
        print(total_revenue, 'none')
        monthly_revenue = Order.objects.filter(order_items__order_status__status="Delivered").annotate(
            month=TruncMonth('purchased_date')
        ).values('month').annotate(
            total_revenue=Sum('total_price')
        ).order_by('month')

        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        current_month_revenue_set = Order.objects.filter(
            order_items__order_status__status="Delivered",
            purchased_date__month=current_month,
            purchased_date__year=current_year
        ).annotate(
            month=TruncMonth('purchased_date')
        ).values('month').annotate(
            total_revenue=Sum('total_price')
        ).order_by('month')

        if current_month_revenue_set.exists():
            current_month_revenue = current_month_revenue_set[0]['total_revenue']
        else:
            current_month_revenue = 0

        total_sales_count = Order.objects.filter(
            order_items__order_status__status="Delivered").count()
        monthly_sales_count = (
            Order.objects
            .filter(order_items__order_status__status="Delivered")
            .annotate(month=TruncMonth('purchased_date'))
            .values('month')
            .annotate(sales_count=Count('id'))
            .order_by('month')
        )
        sales_data = [{'month': item['month'], 'sales_count': item['sales_count']}
                    for item in monthly_sales_count]
        sales_data_json = json.dumps(
            {'sales_data': sales_data}, cls=DateTimeEncoder)
        monthly_sales_count_set = Order.objects.filter(
            order_items__order_status__status="Delivered",
            purchased_date__month=current_month,
            purchased_date__year=current_year
        ).annotate(
            month=TruncMonth('purchased_date')
        ).values('month').annotate(
            sales_count=Count('id')
        ).order_by('month')
        # Get the sales_count for the current month
        if monthly_sales_count_set.exists():
            current_month_sales_count = monthly_sales_count_set[0]['sales_count']
        else:
            current_month_sales_count = 0

        # Transaction
        cod_transaction_count = Payment.objects.filter(
            payment_method__payment_type='COD').count()
        wallet_transaction_count = Payment.objects.filter(
            payment_method__payment_type='Wallet').count()
        online_transaction_count = Payment.objects.filter(
            payment_method__payment_type='Online').count()

        total_transaction_count = cod_transaction_count + \
            wallet_transaction_count + online_transaction_count

        # Calculate the percentages
        if total_transaction_count > 0:
            cod_percentage = (cod_transaction_count /
                            total_transaction_count) * 100
            wallet_percentage = (wallet_transaction_count /
                                total_transaction_count) * 100
            online_percentage = (online_transaction_count /
                                total_transaction_count) * 100
        else:
            cod_percentage = 0
            wallet_percentage = 0
            online_percentage = 0

        top_selling_products = (
            OrderItem.objects
            .values('product__title', 'product__price', 'total_product_price', 'product__featured_image')
            .annotate(
                total_quantity_sold=Sum('quantity'),
                total_revenue=Sum('total_product_price')
            )
            .order_by('-total_quantity_sold')
            [:10]
        )
        top_categories = (
            OrderItem.objects
            .values('product__category__name')
            .annotate(total_products_sold=Count('product'))
            .order_by('-total_products_sold')
            [:10]
        )
        print(top_categories, 'top')
        total_users = CustomUser.objects.filter(is_superuser=False).count()
        total_blocked_users = CustomUser.objects.filter(
            Q(is_superuser=False) & Q(is_blocked=True)).count()
        total_orders = Order.objects.all().count()
        total_pending_order = Order.objects.filter(
            order_items__order_status__status='Pending').count()

        orders_cancel_return = OrderManagement.objects.filter(
            Q(status="return") | Q(status="cancel"))

        print(monthly_sales_count, cod_percentage, 'count')
        context = {
            "title": "Male Fashion | Admin Panel",
            "username": request.user.username if request.user.is_authenticated else None,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "current_month_revenue": current_month_revenue,
            "current_month_sales_count": current_month_sales_count,
            "total_sales_count": total_sales_count,
            "monthly_sales_count": sales_data_json,
            'cod_percentage': round(cod_percentage, 1),
            'wallet_percentage': round(wallet_percentage, 1),
            'online_percentage': round(online_percentage, 1),
            "top_selling_products": top_selling_products,
            "top_categories": top_categories,
            "total_users": total_users,
            "total_blocked_users": total_blocked_users,
            "total_orders": total_orders,
            "total_pending_order": total_pending_order,
            "orders_cancel_return": orders_cancel_return,
        }
        return render(request, 'customadmin/admin-panel.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        print('hi')
        return redirect('customadmin:admin_login')


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            if CustomUser.objects.filter(email=email).exists():
                customer = CustomUser.objects.get(email=email)

                if not customer.is_blocked and customer.is_superuser:
                    user = authenticate(
                        request, email=email, password=password)
                    if user is not None:
                        auth_login(request, user)
                        return redirect("customadmin:admin_panel")
                else:
                    context = {
                        "title": "Login",
                        "error": True,
                        "message": "User is not exists",
                    }
                    return render(
                        request, 'customadmin/admin-login.html', context)

            context = {
                "title": "Login",
                "error": True,
                "message": "Invalid email or password"
            }
            return render(request, 'customadmin/admin-login.html', context)
    else:
        if request.user.is_superuser and request.user.is_authenticated:
            return redirect("customadmin:admin_panel")

        context = {
            "title": "Male Fashion | Admin Login",
        }
        return render(request, 'customadmin/admin-login.html', context)


def admin_logout(request):
    auth_logout(request)
    return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_user(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')

        users = CustomUser.objects.all()

        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        instances = paginate_instances(request, users, per_page=8)
        context = {
            "title": "Male Fashion | Admin User",
            'users': instances,
            'heading': ['First Name', 'Last Name', 'Email', 'Phone Number', 'Superuser', 'Blocked']
        }
        return render(request, 'customadmin/admin-table-user.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        print('hi')
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_user_add(request):
    if request.user.is_superuser and request.user.is_authenticated:
        if request.method == 'POST':
            form = AdminCustomUserForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                is_superuser = form.cleaned_data.get('is_superuser')
                is_blocked = form.cleaned_data.get('is_blocked')

                staff = False
                super_user = False

                if is_superuser:
                    super_user = True
                    staff = True

                CustomUser.objects.create_user(
                    username=instance.first_name,
                    password=instance.password,
                    email=instance.email,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    is_staff=super_user,
                    is_superuser=staff,
                    is_blocked=is_blocked
                )

                return HttpResponseRedirect(reverse("customadmin:admin_user"))
            else:
                message = generate_form_error(form)
                form = AdminCustomUserForm()
                context = {
                    "title": "Male Fashion | Admin Add",
                    "error": True,
                    "message": message,
                    "form": form,
                }
            return render(request, 'customadmin/admin-add.html',
                          context=context)
        else:
            form = AdminCustomUserForm()
            context = {
                "title": "Male Fashion | Admin Add",
                "user_tag": "User",
                "form": form
            }
            return render(request, 'customadmin/admin-add.html', context)

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_user_edit(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        user = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            form = AdminCustomUpdateUserForm(request.POST, instance=user)
            if form.is_valid():
                is_superuser = form.cleaned_data.get('is_superuser')
                is_blocked = form.cleaned_data.get('is_blocked')

                user.is_superuser = is_superuser
                user.is_staff = is_superuser
                user.is_blocked = is_blocked

                form.save()
                return redirect('customadmin:admin_user')
            else:
                message = generate_form_error(form)
                context = {
                    "title": "Male Fashion | Admin Edit",
                    "error": True,
                    "message": message,
                    "form": form,
                    "user": user,
                }
            return render(request, 'customadmin/admin-edit.html', context)
        else:
            form = AdminCustomUpdateUserForm(instance=user)

            context = {
                "title": "Male Fashion | Admin Edit",
                "user": user,
                "form": form,
            }
            return render(request, 'customadmin/admin-edit.html', context)

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_user_block(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        user = get_object_or_404(CustomUser, id=pk)

        user.is_blocked = not user.is_blocked
        user.save()
        response_data = {
            "title": "Successfully Changed",
            "message": "User Updated successfully",
            "status": "success",
        }

        return HttpResponse(json.dumps(response_data),
                            content_type="application/json")

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_user_delete(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    user.delete()

    response_data = {
        "title": "Successfully Changed",
        "message": "User Updated successfully",
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


# Admin Category
# @login_required(login_url="admin-login/")
def admin_category(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')

        categories = Category.objects.filter(is_deleted=False)

        if search_query:
            categories = categories.filter(
                Q(name__icontains=search_query)
            )
        instances = paginate_instances(request, categories, per_page=8)
        context = {
            'categories': instances,
            'heading': ['Name', "Blocked"]
        }
        return render(
            request, 'customadmin/admin-table-category.html', context)

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_category_add(request):
    if request.user.is_superuser and request.user.is_authenticated:
        if request.method == 'POST':
            form = AdminCategory(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                Category.objects.create(name=instance.name)

                return HttpResponseRedirect(
                    reverse("customadmin:admin_category"))
            else:
                print(form)
                message = generate_form_error(form)
                form = AdminCategory()
                context = {
                    "title": "Male Fashion | Admin Category Add",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminCategory()
            context = {
                "title": "Male Fashion | Admin Category Add",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_category_edit(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        category = get_object_or_404(Category, id=pk)
        if request.method == 'POST':
            form = AdminCategory(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("customadmin:admin_category"))
            else:
                message = generate_form_error(form)
                form = AdminCategory()
                context = {
                    "title": "Male Fashion | Admin Category Add",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminCategory(instance=category)
            context = {
                "title": "Male Fashion | Admin Category Add",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, id=pk)
    category.is_deleted = True
    category.save()

    response_data = {
        "title": "Successfully Changed",
        "message": "Category Updated successfully",
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")

# Admin Product
# @login_required(login_url="admin-login/")


def admin_product(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')

        products = Product.objects.all()

        if search_query:
            products = products.filter(Q(title__icontains=search_query))

        instances = paginate_instances(request, products, per_page=8)

        context = {
            'products': instances,
            'heading': ['Title', 'Category', 'Show']
        }
        return render(
            request, 'customadmin/admin-table-products.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_product_add(request):
    if request.user.is_superuser and request.user.is_authenticated:
        ImageFormSet = formset_factory(AdminProductImage, extra=5)

        if request.method == 'POST':
            form = AdminProduct(request.POST, request.FILES)
            formset = ImageFormSet(request.POST, request.FILES)

            if form.is_valid() and formset.is_valid():
                product = form.save()

                for image_form in formset:
                    if image_form.cleaned_data.get('image'):
                        image = image_form.save(commit=False)
                        thumbnail = image_form.save(commit=False)
                        image.product = product
                        thumbnail.save()
                        image.save()

                return HttpResponseRedirect(
                    reverse("customadmin:admin_product"))
            else:
                message = generate_form_error(form)
                context = {
                    'form': form,
                    'formset': formset,
                    'message': message
                }
                return render(
                    request, 'customadmin/admin-product-add.html', context)
        else:
            form = AdminProduct()
            formset = ImageFormSet()
            context = {
                'form': form,
                'formset': formset,
            }
            return render(
                request, 'customadmin/admin-product-add.html', context)

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_product_edit(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        item = get_object_or_404(Product, id=pk)
        product_images = ProductImage.objects.filter(product=item)
        extra_forms = max(0, 5 - product_images.count())
        ImageFormSet = formset_factory(AdminProductImage, extra=extra_forms)

        if request.method == 'POST':
            form = AdminProduct(request.POST, request.FILES, instance=item)
            formset = ImageFormSet(request.POST, request.FILES)

            if form.is_valid() and formset.is_valid():
                form.save()
                feat_image = form.cleaned_data.get('featured_image')
                if feat_image:
                    item.featured_images = feat_image

                item.save()

                for form_index, form in enumerate(formset):
                    clear_checkbox_name = f'form-{form_index}-image-clear'
                    clear_checkbox = request.POST.get(clear_checkbox_name)
                    if clear_checkbox == 'on':
                        product_image = product_images[form_index]
                        product_image.image = None
                        product_image.thumbnail = None
                        product_image.save()

                for i, image_form in enumerate(formset):
                    image_data = image_form.cleaned_data.get('image')
                    if image_data:
                        if i >= product_images.count():
                            ProductImage.objects.create(
                                image=image_data,
                                thumbnail=image_data,
                                product=item
                            )
                        else:
                            product_image = product_images[i]
                            product_image.image = image_data
                            product_image.thumbnail = image_data
                            product_image.save()

                return HttpResponseRedirect(
                    reverse("customadmin:admin_product"))
            else:
                message = generate_form_error(form)
                context = {
                    'form': form,
                    'formset': formset,
                    'message': message
                }
                return render(
                    request, 'customadmin/admin-product-add.html', context)
        else:
            form = AdminProduct(instance=item)
            initial_images = [{'image': image.image}
                              for image in product_images]
            formset = ImageFormSet(initial=initial_images)

            context = {
                'form': form,
                'formset': formset,
            }
            return render(
                request, 'customadmin/admin-product-add.html', context)

    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    product_image = ProductImage.objects.filter(product=product)

    if not product.is_show:
        show = False
    else:
        show = True

    for i in product_image:
        i.is_show = show
        i.save()
    product.is_show = show
    product.save()

    response_data = {
        "title": "Successfully Changed",
        "message": "Product Updated successfully",
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


# Order
def admin_order(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')
        user_filter = request.GET.get('userFilter')
        status_filter = request.GET.get('statusFilter')
        category_filter = request.GET.get('categoryFilter')

        orders = Order.objects.filter(
            ~Q(order_items__order_status__status="Requested For Cancelling") &
            ~Q(order_items__order_status__status="Requested For Returning")
        )

        if search_query:
            orders = orders.filter(Q(user__first_name__icontains=search_query) | Q(
                product__title__icontains=search_query) | Q(order_status__status__icontains=search_query))

        if user_filter:
            orders = orders.filter(user__first_name=user_filter.split(' ')[0], user__last_name=user_filter.split(' ')[1])

        if status_filter:
            orders = orders.filter(order_items__order_status__status=status_filter)

        if category_filter:
            orders = orders.filter(product__category__name=category_filter)

        orders = orders.order_by('-id')

        instances = paginate_instances(request, orders, per_page=8)

        users = CustomUser.objects.all()
        statuses = OrderStatus.objects.all()
        categories = Category.objects.all()

        context = {
            "title": "Male Fashion | Admin Order",
            'heading': ['Full Name', 'Product Title', 'Price', 'Order status', ],
            "orders": instances,
            "users": users,
            "statuses": statuses,
            "categories": categories
        }

        return render(request, 'customadmin/admin-table-order.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_order_details(request, pk):
    order_item = get_object_or_404(OrderItem, id=pk)
    product_order = Order.objects.get(order_items=order_item)
    print(order_item.product, pk,'pro')
    if request.method == 'POST':
        form = AdminOrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            status =  form.cleaned_data['order_status']

            order_item.order_status = status
            order_item.save()

            response_data = {
                "title": "Changed Status",
                "status": "success",
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = AdminOrderItemForm(instance=order_item)

    context = {
        "title": "Male Fashion | My Orders",
        "order": order_item,
        "form": form,
        "product_order": product_order,
    }
    return render(request, 'customadmin/admin-order-page.html', context)



def admin_order_edit(request, pk):
    order = get_object_or_404(OrderItem, id=pk)
    if request.method == 'POST':
        form = AdminOrderItemForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('customadmin:admin_order')
    else:
        form = AdminOrderItemForm(instance=order)
        context = {
            'title': "Male Fashion | Admin Order Edit",
            "form": form
        }

        return render(request, 'customadmin/admin-edit.html', context)


# Product Variant
def admin_product_variant(request):
    if request.user.is_superuser and request.user.is_authenticated:
        variants = ProductVariant.objects.all()

        instances = paginate_instances(request, variants, per_page=6)
        context = {
            "title": "Male Fashion | Product Variant",
            "heading": ['Variant Name', 'Product', 'Stock Unit', 'Size', 'Featured'],
            "variants": instances
        }

        return render(request, 'customadmin/admin-table-variant.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_product_variant_add(request):
    if request.user.is_superuser and request.user.is_authenticated:
        if request.method == 'POST':
            form = AdminProductVariantFrom(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("customadmin:admin_product_variant"))
            else:
                message = generate_form_error(form)
                form = AdminProductVariantFrom()
                context = {
                    "title": "Male Fashion | Admin Product Variant Add",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminProductVariantFrom()
            context = {
                "title": "Male Fashion | Admin Product Variant Add",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_product_variant_edit(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        variant = get_object_or_404(ProductVariant, id=pk)
        if request.method == 'POST':
            form = AdminProductVariantFrom(request.POST, instance=variant)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("customadmin:admin_product_variant"))
            else:
                message = generate_form_error(form)
                form = AdminProductVariantFrom()
                context = {
                    "title": "Male Fashion | Admin Variant Edit",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminProductVariantFrom(instance=variant)
            context = {
                "title": "Male Fashion | Admin Variant Edit",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_product_variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, id=pk)
    variant.is_featured = not variant.is_featured
    variant.save()

    response_data = {
        "title": "Successfully Changed",
        "message": "Variant Updated successfully",
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def admin_contact(request):
    if request.user.is_superuser and request.user.is_authenticated:
        contacts = Contact.objects.all()

        context = {
            "title": "Male Fashion | Contact",
            "heading": ["Name", "Email", "message"],
            "contacts": contacts
        }
        return render(request, 'customadmin/admin-table-contact.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_banner(request):
    if request.user.is_superuser and request.user.is_authenticated:
        banners = Banner.objects.all()

        context = {
            "title": "Male Fashion | Banner",
            "heading": ["Title", "Category", "Featured"],
            "banners": banners
        }

        return render(request, 'customadmin/admin-table-banner.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_banner_add(request):
    if request.user.is_superuser and request.user.is_authenticated:
        if request.method == 'POST':
            form = AdminBannerForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("customadmin:admin_banner"))
            else:
                message = generate_form_error(form)
                form = AdminBannerForm()
                context = {
                    "title": "Male Fashion | Admin Banner Add",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminBannerForm()
            context = {
                "title": "Male Fashion | Admin Banner Add",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_banner_edit(request, pk):
    if request.user.is_superuser and request.user.is_authenticated:
        banner = get_object_or_404(Banner, id=pk)
        if request.method == 'POST':
            form = AdminBannerForm(
                request.POST, request.FILES, instance=banner)
            if form.is_valid():
                instance = form.save(commit=False)
                if 'image' in request.FILES:
                    instance.image = request.FILES['image']

                instance.save()

                return HttpResponseRedirect(
                    reverse("customadmin:admin_banner"))
            else:
                message = generate_form_error(form)
                form = AdminBannerForm()
                context = {
                    "title": "Male Fashion | Admin Variant Edit",
                    "error": True,
                    "message": message,
                    "form": form,
                }
                return render(
                    request, 'customadmin/admin-add.html', context=context)
        else:
            form = AdminBannerForm(instance=banner)
            context = {
                "title": "Male Fashion | Admin Variant Edit",
                "form": form,
            }
            return render(request, 'customadmin/admin-add.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_banner_delete(request, pk):
    banner = get_object_or_404(Banner, id=pk)
    banner.is_featured = not banner.is_featured
    banner.save()

    response_data = {
        "title": "Successfully Changed",
        "message": "Variant Updated successfully",
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def admin_order_center(request):
    title = request.GET.get('title', '')

    valid_statuses = ['return', 'cancel', 'completed', 'approved']

    orders = OrderManagement.objects.filter(Q(status__in=valid_statuses))

    if title:
        orders = orders.filter(ordered_product__product__title=title)

    context = {
        "title": "Male Fashion | Admin Order Resolution",
        "heading": ['Product', 'Reason', 'Status'],
        "orders": orders
    }
    return render(request, 'customadmin/admin-table-returned.html', context)


def admin_order_center_edit(request, pk):
    pass


def admin_order_center_approve(request, pk):
    order = get_object_or_404(OrderManagement, id=pk)

    purchased_order = Order.objects.get(order_items=order.ordered_product)
    payment = Payment.objects.get(order=purchased_order)

    if payment.payment_method.payment_type == "COD":
        product_variant = ProductVariant.objects.get(
            product=order.ordered_product.product,
            size=order.ordered_product.size)
        product_variant.stock_unit += order.ordered_product.quantity
        product_variant.save()

        order_data = Order.objects.get(order_items=order.ordered_product)
        print(order_data, 'order')
        wallet = Wallet.objects.get(user=order_data.user)
        wallet.balance += order.ordered_product.total_product_price
        wallet.save()

        purchased_order = Order.objects.get(order_items=order.ordered_product)

        WalletHistory.objects.create(
            order=purchased_order,
            description="Amount for this order Amount is Credited",
            wallet=wallet,
            amount=order.ordered_product.total_product_price,
            transaction_operation='credit'
        )

        order_status = OrderStatus.objects.get(status="Refunded")
        order.ordered_product.order_status = order_status
        order.ordered_product.save()

        order.status = "completed"
        order.save()

        send_user_refund_mail(
            request,
            order.ordered_product.total_product_price,
            order_data.user.email)

        response_data = {
            "title": "Amount Refunded",
            "order_status": order.status,
            "status": "success",
        }

        return HttpResponse(json.dumps(response_data),
                            content_type="application/json")
    else:
        order_status = OrderStatus.objects.get(status="Approved")
        order.ordered_product.order_status = order_status
        order.ordered_product.save()

        order.status = "approved"
        order.save()

        response_data = {
            "title": "Approved Returned",
            "order_status": order.status,
            "status": "success",
        }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def admin_order_center_completed(request, pk):
    order = get_object_or_404(OrderManagement, id=pk)

    product_variant = ProductVariant.objects.get(
        product=order.ordered_product.product,
        size=order.ordered_product.size)
    product_variant.stock_unit += order.ordered_product.quantity
    product_variant.save()

    order_data = Order.objects.get(order_items=order.ordered_product)
    print(order_data, 'order')

    wallet = Wallet.objects.get(user=order_data.user)
    wallet.balance += order.ordered_product.total_product_price
    wallet.save()

    purchased_order = Order.objects.get(order_items=order.ordered_product)

    WalletHistory.objects.create(
        order=purchased_order,
        description="Amount for this order Amount is Credited",
        wallet=wallet,
        amount=order.ordered_product.total_product_price,
        transaction_operation='credit'
    )

    order_status = OrderStatus.objects.get(status="Refunded")
    order.ordered_product.order_status = order_status
    order.ordered_product.save()

    order.status = "completed"
    order.save()

    send_user_refund_mail(
        request,
        order.ordered_product.total_product_price,
        order_data.user.email)

    response_data = {
        "title": "Amount Refunded",
        "order_status": order.status,
        "status": "success",
    }

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


# Coupon
def admin_coupon(request):
    coupons = Coupon.objects.all()

    context = {
        "title": "Male Fashion | Admin Coupon",
        "heading": ['Coupon', 'Discount Type', 'Amount or Percentage', 'Valid From', 'Valid To'],
        "coupons": coupons
    }

    return render(request, 'customadmin/admin-table-coupon.html', context)


def admin_coupon_add(request):
    if request.method == 'POST':
        form = AdminCouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_coupon")
    else:
        form = AdminCouponForm()
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


def admin_coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, id=pk)
    if request.method == 'POST':
        form = AdminCouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_coupon")
    else:
        form = AdminCouponForm(instance=coupon)
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


def admin_sales_report(request):
    order_status = request.GET.get('order_status')

    if order_status:
        orders = Order.objects.filter(
            order_items__order_status__status=order_status)
    else:
        orders = Order.objects.all()

    if request.method == 'POST':
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']

        request.session['from_date'] = from_date
        request.session['to_date'] = to_date

        filtered_orders = orders.filter(
            purchased_date__range=[
                from_date, to_date])

        context = {
            "title": "Male Fashion | Sales Report",
            "orders": filtered_orders,
        }

        return render(request, 'customadmin/admin-sales-report.html', context)
    else:
        context = {
            "title": "Male Fashion | Sales Report",
            "orders": orders
        }

        return render(request, 'customadmin/admin-sales-report.html', context)


def download_sales_report_csv(request):
    order_status = request.GET.get('order_status')

    from_date = request.session.get('from_date')
    to_date = request.session.get('to_date')

    if from_date and to_date:
        if order_status:
            orders = Order.objects.filter(
                order_items__order_status__status=order_status,
                purchased_date__range=[from_date, to_date]
            )
        else:
            orders = Order.objects.filter(
                purchased_date__range=[from_date, to_date]
            )
    elif order_status:
        orders = Order.objects.filter(
            order_items__order_status__status=order_status)
    else:
        orders = Order.objects.all()

    data_to_export = orders

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer Name', 'Total Price',
                    'Product', 'Order Status', 'Purchase Date'])

    all_status = []
    all_product = []

    for order in data_to_export:
        status = []
        product = []

        for item in order.order_items.all():
            status.append(item.order_status.status)
            product.append(f"{item.product} ({item.quantity})")

        all_status.append(status)
        all_product.append(product)

        writer.writerow([
            order.id,
            f"{order.user.first_name} {order.user.last_name}",
            order.total_price,
            ', '.join(product),
            ', '.join(status),
            order.purchased_date
        ])

    return response


#Category Offer
def admin_category_offer(request):
    category_offers = CategoryOffer.objects.filter(active=True)

    context = {
        "title": "Male Fashion | Admin Coupon",
        "heading": ['Category', 'Discount Type', 'Amount or Percent', 'From Date',"Expiry Date"],
        "category_offers": category_offers
    }

    return render(request, 'customadmin/admin-category-offer.html', context)


def admin_category_offer_add(request):
    if request.method == 'POST':
        form = AdminCategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_category_offer")
    else:
        form = AdminCategoryOfferForm()
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


def admin_category_offer_edit(request, pk):
    category_offer = get_object_or_404(CategoryOffer, id=pk)
    if request.method == 'POST':
        form = AdminCategoryOfferForm(request.POST, instance=category_offer)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_category_offer")
    else:
        form = AdminCategoryOfferForm(instance=category_offer)
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)
    

#Product Offer
def admin_product_offer(request):
    product_offers = ProductOffer.objects.filter(active=True)

    context = {
        "title": "Male Fashion | Admin Coupon",
        "heading": ['Product', 'Discount Type', 'Amount or Percent', "Valid From","Expiry Date"],
        "product_offers": product_offers
    }

    return render(request, 'customadmin/admin-product-offer.html', context)


def admin_product_offer_add(request):
    if request.method == 'POST':
        form = AdminProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_product_offer")
    else:
        form = AdminProductOfferForm()
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


def admin_product_offer_edit(request, pk):
    product_offer = get_object_or_404(ProductOffer, id=pk)
    if request.method == 'POST':
        form = AdminProductOfferForm(request.POST, instance=product_offer)
        if form.is_valid():
            form.save()
            return redirect("customadmin:admin_product_offer")
    else:
        form = AdminProductOfferForm(instance=product_offer)
        context = {
            "title": "Male Fashion | Admin Coupon Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)
    

#Review
def admin_reviews(request):
    reviews = UserReview.objects.all()

    context = {
        "title": "Male Fashion | Admin Reviews",
        "heading": ['Product', 'Username', 'Message', 'Reply'],
        "reviews": reviews,
    }
    return render(request, 'customadmin/admin-table-reviews.html', context)
    

def admin_review_reply(request, pk):
    review = UserReview.objects.get(id=pk)

    if request.method == 'POST':
        form = AdminReviewForm(request.POST)
        if form.is_valid():
            form.save()

            response_data = {
                "title": "Reply Added",
                "status": "success"
            }
        else:
            response_data = {
                "title": "Error",
                "status": "error"
            }
        return HttpResponse(json.dumps(response_data),content_type="application/json")
    
    else:
        form = AdminReviewForm(instance=review)
        context = {
            "title": "Male Fashion | Admin Reply Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


#Referral Offer
def admin_referral_offer(request):
    referral = ReferralAmount.objects.first()

    context = {
        "title": "Male Fashion | Admin Referral",
        "heading": ["Referral Amount", "Gain Amount" ],
        "referral": referral,
    }

    return render(request, 'customadmin/admin-table-referral.html', context)


def admin_referral_offer_edit(request):
    referral = ReferralAmount.objects.first()

    if request.method == 'POST':
        form = AdminReferralAmountForm(request.POST, instance=referral)
        if form.is_valid():
            form.save()

            response_data = {
                "title": "Reply Added",
                "status": "success"
            }
        else:
            response_data = {
                "title": "Error",
                "status": "error"
            }
        return redirect("customadmin:admin_referral_offer")
    
    else:
        form = AdminReferralAmountForm(instance=referral)
        context = {
            "title": "Male Fashion | Admin Reply Add",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)
    

#Notification
def admin_notification(request):
    notifications = BroadcastNotification.objects.all()

    context = {
        "title": "Male Fashion | Admin Notification",
        "heading": ["Message", "Broadcast On", "Sended"],
        "notifications": notifications,
    }

    return render(request, 'customadmin/admin-table-notification.html', context)

def admin_notification_add(request):
    if request.method == 'POST':
        form = AdminBroadcastNotificationForm(request.POST)
        if form.is_valid():
            form.save()

            response_data = {
                "title": "Reply Added",
                "status": "success"
            }
        else:
            response_data = {
                "title": "Error",
                "status": "error"
            }
        return redirect("customadmin:admin_notification")
    
    else:
        form = AdminBroadcastNotificationForm()
        context = {
            "title": "Male Fashion | Admin Notification",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


def admin_notification_edit(request, pk):
    notification = BroadcastNotification.objects.get(id=pk)
    if request.method == 'POST':
        form = AdminBroadcastNotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()

            response_data = {
                "title": "Reply Added",
                "status": "success"
            }
        else:
            response_data = {
                "title": "Error",
                "status": "error"
            }
        return redirect("customadmin:admin_notification")
    
    else:
        form = AdminBroadcastNotificationForm(instance=notification)
        context = {
            "title": "Male Fashion | Admin Notification",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)
