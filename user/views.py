from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from user.models import CustomUser
from user.forms import CustomUserForm
from user.functions import generate_form_error



def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)

                return redirect("web:index")
        
        context = {
            "title" : "Login",
            "error" : True,
            "message" : "Invalid email or password"
        }
        return render(request, 'auth/user_login.html', context=context)    
    else:
        if request.user.is_authenticated:
            return redirect("web:index")
        
        context = {
            "title" : "Login",
        }
        return render(request, 'user/login.html', context=context)


def signup(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            user = CustomUser.objects.create_user(
                username=instance.first_name,
                password=instance.password,
                email=instance.email,
                first_name=instance.first_name,
                last_name = instance.last_name,
                phone_number=instance.phone_number,
            )

            user = authenticate(request, email=instance.email, password=instance.password)
            auth_login(request, user)

            return redirect("web:index")
        else:
            message = generate_form_error(form)
            form = CustomUserForm()
            context = {
                "title" : "Male Fashion | Signup",
                "error" : True,
                "message" : message,
                "form": form,
            }
        return render(request, 'user/signup.html', context)
    else:
        form = CustomUserForm()
        context = {
            "Title" : "Male Fashion | Signup",
            "form" : form,
        }
        return render(request, 'user/signup.html', context)


def otp_login(request, *args, **kwargs):
    return render(request, 'user/otp.html')


def logout(request):
    auth_logout(request)
    return redirect("web:index")