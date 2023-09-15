from django.urls import path
from user import views


app_name = "user"


urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('otp_login/', views.otp_login, name='otp_login'),
]