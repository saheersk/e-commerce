import json
import pyotp
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponse
from django.conf import settings
from decimal import Decimal

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from shop.models import WalletHistory
from user.models import CustomUser, Wallet, ReferralAmount
from user.forms import CustomUserForm
from main.functions import generate_form_error
from user.utils import send_otp
from user_profile.forms import PasswordResetRequestForm


User = get_user_model()


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
            
            used_code =  form.cleaned_data['used_code']
            password = make_password(instance.password)
            
            instance.password = password
            base_username = f"{instance.first_name}_{instance.last_name}"
            username = base_username
            i = 1

            while CustomUser.objects.filter(username=username).exists():
                username  = f"{base_username}_{i}"
                i += 1
            
            instance.username = username
            instance.save()

            user_wallet = Wallet.objects.create(user=instance)

            referred_amount = ReferralAmount.objects.first()

            if CustomUser.objects.filter(referral_code=used_code).exists():
                referred_user = CustomUser.objects.get(referral_code=used_code)
                referred_user_wallet = Wallet.objects.get(user=referred_user)
                referred_user_wallet.balance += Decimal(referred_amount.referred_user_amount)
                referred_user_wallet.save()

                if used_code:
                    user_wallet.balance = Decimal(user_wallet.balance)
                    user_wallet.balance += Decimal(referred_amount.new_user_amount)
                    user_wallet.save()

                WalletHistory.objects.create(
                            wallet=user_wallet,
                            description= f"Referral Amount Credited From user {instance.first_name}",
                            amount=referred_amount.new_user_amount,
                            transaction_operation='credit'
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
                totp = pyotp.TOTP(otp_secret_key, interval=180)
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


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return HttpResponse("User with this email does not exist.")

            token = default_token_generator.make_token(user)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = reverse('user:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

            subject = 'Password Reset'
            message = f'Click the following link to reset your password:\n{request.build_absolute_uri(reset_url)}'
            from_email = 'saheerabcd3@gmail.com'  #
            recipient_list = [user.email]  

            msg = Mail(
                from_email=from_email,
                to_emails=recipient_list,
                subject=subject,
                plain_text_content=message
            )

            try:
                sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                response = sg.send(msg)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(str(e))

            return redirect('user:password_reset_done') 
    else:
        form = PasswordResetRequestForm()

    return render(request, 'user/forgot-password/password_reset_request.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect('user:password_reset_complete') 
            else:
                return HttpResponse('Passwords do not match. Please try again.')
        else:
            return render(request, 'user/forgot-password/password_reset_confirm.html')
    else:
        return HttpResponse('Password reset link is invalid or has expired.')