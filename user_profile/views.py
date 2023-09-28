import re
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash

from user.models import Address 
from user_profile.forms import CustomUserEditForm
from main.functions import generate_form_error

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
            # if form.cleaned_data.get('profile_picture'):
            #     user.profile_picture = form.cleaned_data.get('profile_picture')
            # user.save()
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                print(user.profile_picture, 'pic')

            user.save()

            response_data = {
                "status" : "success",
                "title" : "Successfully Changed Password",
                "message" : 'Password was successfully changed',
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

