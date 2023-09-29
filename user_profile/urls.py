from django.urls import path
from user_profile import views


app_name = "user_profile"


urlpatterns = [
    path('profile/', views.profile_details, name='profile_details'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.profile_change_password, name='profile_change_password'),

    #address
    path('address/', views.profile_address, name='profile_address'),
    path('address/add/', views.profile_address_add, name='profile_address_add'),
    path('address/edit/<int:pk>/', views.profile_address_edit, name='profile_address_edit'),
    path('address/delete/<int:pk>/', views.profile_address_delete, name='profile_address_delete'),
    path('address/default/<int:pk>/', views.profile_address_default, name='profile_address_default'),

    #My order
    path('my-order/', views.profile_order, name='profile_order'),
    path('my-order/cancel/<int:pk>/', views.profile_order_cancel, name='profile_order_cancel'),
]