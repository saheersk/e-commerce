from django.urls import path
from django.contrib.auth import views as auth_views

# from sendgrid_backend import SendgridBackend

from user import views


app_name = "user"


urlpatterns = [
    #authentication
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),

    #otp
    path('otp-sent/', views.otp_sent, name='otp_sent'),
    path('otp-resend/', views.otp_resend, name='otp_resend'),
    path('otp-verify/', views.otp_verify, name='otp_verify'),

    #Reset password
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user/forgot-password/password_reset_complete.html'), name='password_reset_complete'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='user/forgot-password/password_reset_done.html'), name='password_reset_done'),
]