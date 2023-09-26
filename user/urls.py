from django.urls import path
from user import views


app_name = "user"


urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('otp-sent/', views.otp_sent, name='otp_sent'),
    path('otp-resend/', views.otp_resend, name='otp_resend'),
    path('otp-verify/', views.otp_verify, name='otp_verify'),
]