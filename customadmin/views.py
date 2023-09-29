import json

from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.forms import formset_factory

from customadmin.forms import AdminCustomUserForm, AdminCustomUpdateUserForm, AdminCategory, AdminProduct, AdminProductImage, AdminOrderFrom
from user.models import CustomUser
from user.functions import generate_form_error
from shop.models import Category, Product, ProductImage, Order


#Admin User
# @login_required(login_url="admin-login/")
def admin_panel(request):
    if request.user.is_superuser and request.user.is_authenticated:
        context = {
            "title": "Male Fashion | Admin Panel",
            "username": request.user.username if request.user.is_authenticated else None,
        }
        return render(request, 'customadmin/admin-panel.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            if CustomUser.objects.filter(email=email).exists():
                customer = CustomUser.objects.get(email=email)

                if customer.is_blocked == False and customer.is_superuser:
                    user = authenticate(request, email=email, password=password)
                    if user is not None:
                        auth_login(request, user)
                        return redirect("customadmin:admin_panel")
                else:
                    context = {
                        "title" : "Login",
                        "error" : True,
                        "message" : "User is not exists",
                    }
                    return render(request, 'customadmin/admin-login.html', context)
            
            context = {
                "title" : "Login",
                "error" : True,
                "message" : "Invalid email or password"
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

        context = {
            "title": "Male Fashion | Admin User",
            'users': users,
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
                        last_name = instance.last_name,
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
                    "error" : True,
                    "message" : message,
                    "form": form,
                }
            return render(request, 'customadmin/admin-add.html', context=context)
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
                    "error" : True,
                    "message" : message,
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
            "title" : "Successfully Changed",
            "message" : "User Updated successfully",
            "status" : "success",
        }

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')
    

# @login_required(login_url="admin-login/")
def admin_user_delete(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    user.delete()

    response_data = {
        "title" : "Successfully Changed",
        "message" : "User Updated successfully",
        "status" : "success",
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


#Admin Category
# @login_required(login_url="admin-login/")
def admin_category(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')

        categories = Category.objects.filter(is_deleted=False)

        if search_query:
            categories = categories.filter(
                Q(name__icontains=search_query)
            )
        context = {
            'categories': categories,
            'heading': ['Name', "Blocked"]
        }
        return render(request, 'customadmin/admin-table-category.html', context)

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

                return HttpResponseRedirect(reverse("customadmin:admin_category"))
            else:
                print(form)
                message = generate_form_error(form)
                form = AdminCategory()
                context = {
                    "title": "Male Fashion | Admin Category Add",
                    "error" : True,
                    "message" : message,
                    "form": form,
                }
                return render(request, 'customadmin/admin-add.html', context=context)
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
                return HttpResponseRedirect(reverse("customadmin:admin_category"))
            else:
                message = generate_form_error(form)
                form = AdminCategory()
                context = {
                    "title": "Male Fashion | Admin Category Add",
                    "error" : True,
                    "message" : message,
                    "form": form,
                }
                return render(request, 'customadmin/admin-add.html', context=context)
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
            "title" : "Successfully Changed",
            "message" : "Category Updated successfully",
            "status" : "success",
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")

#Admin Product
# @login_required(login_url="admin-login/")
def admin_product(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')

        products = Product.objects.all()

        if search_query:
            products = products.filter( Q(title__icontains=search_query))

        context = {
            'products': products,
            'heading': ['Title', 'Category', 'Stock Unit', 'Show']
        }
        return render(request, 'customadmin/admin-table-products.html', context)
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

                return HttpResponseRedirect(reverse("customadmin:admin_product"))
            else:
                message = generate_form_error(form)
                context = {
                    'form': form,
                    'formset': formset,
                    'message': message
                }
                return render(request, 'customadmin/admin-product-add.html', context)
        else:
            form = AdminProduct()
            formset = ImageFormSet()
            context = {
                'form': form,
                'formset': formset,
            }
            return render(request, 'customadmin/admin-product-add.html', context)

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

                return HttpResponseRedirect(reverse("customadmin:admin_product"))
            else:
                message = generate_form_error(form)
                context = {
                    'form': form,
                    'formset': formset,
                    'message': message
                }
                return render(request, 'customadmin/admin-product-add.html', context)
        else:
            form = AdminProduct(instance=item)
            initial_images = [{'image': image.image} for image in product_images]
            formset = ImageFormSet(initial=initial_images)

            context = {
                'form': form,
                'formset': formset,
            }
            return render(request, 'customadmin/admin-product-add.html', context)
    
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


# @login_required(login_url="admin-login/")
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    product_image = ProductImage.objects.filter(product=product)
    
    if product.is_show == True:
        show = False
    else:
        show = True

    for i in product_image:
            i.is_show = show
            i.save()
    product.is_show = show
    product.save()

    response_data = {
            "title" : "Successfully Changed",
            "message" : "Product Updated successfully",
            "status" : "success",
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


#Order
def admin_order(request):
    if request.user.is_superuser and request.user.is_authenticated:
        search_query = request.GET.get('search')


        orders = Order.objects.all()
        if search_query:
            orders = orders.filter(Q(user__first_name__icontains=search_query) | Q(product__title__icontains=search_query) | Q(order_status__status__icontains=search_query))
              
        context = {
            "title" : "Male Fashion | Admin Order",
            'heading': ['Full Name', 'Product Title', 'Price', 'Order status', ],
            "orders" : orders
        }

        return render(request, 'customadmin/admin-table-order.html', context)
    elif request.user.is_authenticated:
        return redirect('web:index')
    else:
        return redirect('customadmin:admin_login')


def admin_order_edit(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == 'POST':
        form = AdminOrderFrom(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('customadmin:admin_order')
    else:
        form = AdminOrderFrom(instance=order)
        context = {
            'title' : "Male Fashion | Admin Order Edit",
            "form" : form
        }

        return render(request, 'customadmin/admin-edit.html', context)