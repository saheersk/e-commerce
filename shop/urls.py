from django.urls import path
from shop import views


app_name = "shop"


urlpatterns = [
    path('all/', views.product_all, name='product_all'),
    path('<str:slug>/', views.product_details, name='product_details'),
]