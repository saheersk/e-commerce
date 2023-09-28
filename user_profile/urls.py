from django.urls import path
from user_profile import views


app_name = "user_profile"


urlpatterns = [
    path('profile/', views.profile_details, name='profile_details'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.profile_change_password, name='profile_change_password'),
]