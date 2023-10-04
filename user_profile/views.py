import re
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash

from user.models import Address 
from user_profile.forms import CustomUserEditForm
from main.functions import generate_form_error
from user_profile.forms import AddressForm, OrderManagementForm
from shop.models import Order, Cart, OrderStatus, OrderItem, Payment


@login_required(login_url='user/login/')
def profile_details(request):
    if request.user.is_authenticated:
        user = request.user
        default_address = Address.objects.get(user=user, is_default=True)
    context = {
        "title": "Male Fashion | Profile Detail",
        "user": user,
        "default_address" : default_address
    }

    return render(request, 'profile/user-profile.html', context)


@login_required(login_url='user/login/')
def profile_change_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
    else:
        context = {
            "title": "Male Fashion | Change Password",
        }

        return render(request, 'profile/change-password.html', context)
    

@login_required(login_url='user/login/')
def profile_change_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if len(password) < 8:
            response_data = {
                "message": 'Password must contain at least 8 characters.',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if password == "" or confirm_password == "":
            response_data = {
                "message" : 'Password is required',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if not re.search(r'[A-Z]', password):
            response_data = {
                "message" : 'Password must contain at least one uppercase letter.',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if not re.search(r'[0-9]', password):
            response_data = {
                "message" : 'Password must contain at least one numeric digit.',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        
        if not re.search(r'[!@#$%^&*()_+{}[\]:;<>,.?~\\]', password):
            response_data = {
                "message" : 'Password must contain at least one special character.',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if password != confirm_password:
            response_data = {
                "message" : 'Passwords do not match.',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        
        user = request.user

        user.set_password(password)
        user.save()

        update_session_auth_hash(request, user)

        response_data = {
                "status" : "success",
                "title" : "Successfully Changed Password",
                "message" : 'Password was successfully changed',
                "redirect" : "yes",
                "redirect_url": '/user-profile/profile/',
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        context = {
            "title": "Male Fashion | Change Password",
        }

        return render(request, 'profile/change-password.html', context)
    

@login_required(login_url='user/login/')
def profile_edit(request):
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)  
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                print(user.profile_picture, 'pic')

            user.save()

            response_data = {
                "status" : "success",
                "title" : "Successfully Updated",
                "message" : 'Profile has been updated successfully',
                "redirect" : "yes",
                "redirect_url": '/user-profile/profile/',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            message = generate_form_error(form)
            form = CustomUserEditForm(instance=request.user)
            context = {
                "status" : "error",
                "title": "Male Fashion | Edit Profile",
                "message": str(message),
                "form": form
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = CustomUserEditForm(instance=request.user)  
        context = {
            "title": "Male Fashion | Edit Profile",
            "form": form,
        }
        return render(request, 'profile/edit-profile.html', context)
    


@login_required(login_url='user/login/')
def profile_address_add(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            print(instance, 'instance')

            default = request.POST.get('is_default')
            if default == 'on':
                address = Address.objects.get(user=request.user, is_default=True)
                address.is_default = False
                address.save()
                instance.is_default = True

            instance.user = request.user
            instance.save()

            response_data = {
                "status" : "success",
                "title" : "Successfully Updated",
                "message" : 'Profile has been updated successfully',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            error_message = generate_form_error(form)
            response_data = {
                "status" : "error",
                "title" : "Address Field Error.",
                "message" : str(error_message),
                }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = AddressForm()
        context = {
            "title" : "Male Fashion | Address",
            "form" : form,
        }

        return render(request, 'user/address-input.html', context)


@login_required(login_url='user/login/')
def profile_address(request):
    addresses = Address.objects.filter(user=request.user, is_default=False)
    default_address = Address.objects.get(user=request.user, is_default=True)

    context = {
        "title" : "Male Fashion | My Address",
        "addresses" : addresses,
        "default_address" : default_address

    }
    return render(request, 'profile/user-address.html', context)


@login_required(login_url='user/login/')
def profile_address_edit(request, pk):
    address = get_object_or_404(Address, id=pk)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            instance = form.save(commit=False)

            default = request.POST.get('is_default')
            if default == 'on':
                address = Address.objects.get(user=request.user, is_default=True)
                address.is_default = False
                address.save()
                instance.is_default = True

            instance.user = request.user
            instance.save()

            response_data = {
                "status" : "success",
                "title" : "Successfully Updated",
                "message" : 'Profile has been updated successfully',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            error_message = generate_form_error(form)
            response_data = {
                "status" : "error",
                "title" : "Address Field Error.",
                "message" : str(error_message),
                }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = AddressForm(instance=address)
        context = {
            "error" : False,
            "title" : "Male Fashion | Address",
            "form" : form,
        }

        return render(request, 'profile/edit-address.html', context)
    

@login_required(login_url='user/login/')
def profile_address_default(request, pk):
    address = get_object_or_404(Address, id=pk)
    default_address = Address.objects.get(user=request.user, is_default=True)

    default_address.is_default = False
    address.is_default = True

    address.save()
    default_address.save()

    response_data = {
        "status" : "success",
        "title" : "Address Updated",
        "message" : 'Password was successfully changed',
    }
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required(login_url='user/login/')
def profile_address_delete(request, pk):
    address = get_object_or_404(Address, id=pk)

    if address.is_default == False:
        address.delete()

    response_data = {
        "status" : "success",
        "title" : "Successfully deleted",
        "message" : 'Address was successfully deleted',
    }
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required(login_url='user/login/')
def profile_order(request):
    if request.method == "POST":
        pass
    else:
        orders = Order.objects.filter(user=request.user).order_by('-id')

        request.session['cart_count'] = Cart.objects.filter(user=request.user, is_deleted=False).count() if request.user.is_authenticated else 0

        context = {
            "title" : "Male Fashion | My Orders",
            "orders" : orders,
        }
        return render(request, 'profile/user-order.html', context)
    

@login_required(login_url='user/login/')
def profile_order_details(request, pk):
    orders = Order.objects.filter(user=request.user, id=pk)
    context = {
        "title" : "Male Fashion | My Orders",
        "orders" : orders
    }
    return render(request, 'profile/user-order-details.html', context)


@login_required(login_url='user/login/')
def profile_order_cancel(request, pk):
    product = get_object_or_404(OrderItem, id=pk)

    order = Order.objects.get(user=request.user, order_items=product)

    payment = Payment.objects.get(order=order)
    
    if request.method == 'POST':
        form = OrderManagementForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.ordered_product = product 
            if payment.payment_method.payment_type== "COD":
                instance.status = "cancelled"

                status = OrderStatus.objects.get(status="Cancelled")
                product.order_status = status
                product.save()
            else:
                instance.status = "requested for cancel"

                status = OrderStatus.objects.get(status="Requested For Cancelling")
                product.order_status = status
                product.save()

            instance.save()

            response_data = {
                "status": "success",
                "title": "Successfully Cancelled",
                "message": 'Your Product has been Cancelled',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            error_message = generate_form_error(form)
            print(error_message, 'error')
            response_data = {
                "status" : "error",
                "title" : "Address Field Error.",
                "message" : str(error_message),
                }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = OrderManagementForm()
        context = {
            "title": "Male Fashion | Product Cancel",
            "product": product,
            "form": form
        }

        return render(request, 'profile/user-order-cancel.html', context)




@login_required(login_url='user/login/')
def profile_order_return(request, pk):
    product = get_object_or_404(OrderItem, id=pk)

    order = Order.objects.get(user=request.user, order_items=product)

    payment = Payment.objects.get(order=order)
    
    if request.method == 'POST':
        form = OrderManagementForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.ordered_product = product 

            instance.status = "requested for return"

            status = OrderStatus.objects.get(status="Requested For Returning")
            product.order_status = status
            product.save()

            instance.save()

            response_data = {
                "status": "success",
                "title": "Successfully Cancelled",
                "message": 'Your Product has been Cancelled',
            }

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            error_message = generate_form_error(form)
            print(error_message, 'error')
            response_data = {
                "status" : "error",
                "title" : "Address Field Error.",
                "message" : str(error_message),
                }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        form = OrderManagementForm()
        context = {
            "title": "Male Fashion | Product Return",
            "product": product,
            "form": form
        }

        return render(request, 'profile/user-order-return.html', context)
    