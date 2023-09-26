import pyotp
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password

from user.models import CustomUser
from user.forms import CustomUserForm
from user.functions import generate_form_error
from user.utils import send_otp


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            if  CustomUser.objects.filter(email=email).exists():
                customer = CustomUser.objects.get(email=email)

                if customer.is_blocked == False:
                    user = authenticate(request, email=email, password=password)
                    if user is not None:
                        auth_login(request, user)

                        return redirect("web:index")
                else:
                    context = {
                        "title" : "Login",
                        "error" : True,
                        "message" : "User is blocked",
                    }
                    return render(request, 'user/login.html', context=context)  
            
            context = {
                "title" : "Login",
                "error" : True,
                "message" : "Invalid email or password"
            }
            return render(request, 'user/login.html', context=context)    
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

            password = make_password(instance.password)

            user = CustomUser.objects.create_user(
                username=instance.first_name,
                password=password,
                email=instance.email,
                first_name=instance.first_name,
                last_name = instance.last_name,
                phone_number=instance.phone_number,
            )
            
            request.session['email'] = instance.email
            send_otp(request, instance.email)

            return redirect("user:otp_verify")
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
        if request.user.is_authenticated:
            return redirect("web:index")
        
        form = CustomUserForm()
        context = {
            "Title" : "Male Fashion | Signup",
            "form" : form,
        }
        return render(request, 'user/signup.html', context)


def otp_sent(request, *args, **kwargs):
    message = None
    if request.method == "POST":
        email = request.POST.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            if user.is_blocked == False:
                send_otp(request, email)
                request.session['email'] = email
                return redirect('user:otp_verify')
            else:
                message = "User is Blocked"
                context = {
                    'title' : "Male Fashion | Otp",
                    'message' : message
                }
                return render(request, 'user/otp-sent.html', context)
        else:
            message = "User not exist."
            context = {
                'title' : "Male Fashion | Otp",
                'message' : message
            }
            return render(request, 'user/otp-sent.html', context)
    else:
        if request.user.is_authenticated:
            return redirect("web:index")
        
        context = {
            'title' : "Male Fashion | Otp",
        }
        return render(request, 'user/otp-sent.html', context)
    

def otp_resend(request):
    email = request.session.get('email')
    send_otp(request, email)
    return redirect('user:otp_verify')


def otp_verify(request, *args, **kwargs):
    error_message = None 

    if request.method == 'POST':
        otp = request.POST.get('otp')
        email = request.session.get('email')

        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_date = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_date is not None:
            valid_unit = datetime.fromisoformat(otp_valid_date)

            if valid_unit > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                print(totp.verify(otp))
                if totp.verify(otp):
                    user = get_object_or_404(CustomUser, email=email)
                    authenticate(request, email=user.email, password=user.password)
                    auth_login(request, user)
                    return redirect('web:index')
                else:
                    error_message = "Incorrect password."
            else:
                error_message = "Invalid OTP. Please try again."
        else:
            error_message = "OTP has expired. Please request a new one."  

    if request.user.is_authenticated:
            return redirect("web:index")
    
    context = {"error_message": error_message}

    return render(request, 'user/otp-verify.html', context)


def logout(request):
    auth_logout(request)
    return redirect("web:index")