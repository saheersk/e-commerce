from django.urls import path
from shop import views


app_name = "shop"


urlpatterns = [
    #Product
    path('all/', views.product_all, name='product_all'),
    path('<str:slug>/', views.product_details, name='product_details'),

    #Wishlist
    path('user/wishlist/', views.product_wishlist, name='product_wishlist'),
    path('user/wishlist/add/<int:pk>/', views.product_wishlist_add, name='product_wishlist_add'),
    path('user/wishlist/remove/<int:pk>/', views.product_wishlist_remove, name='product_wishlist_remove'),

    #Cart
    path('user/cart/', views.product_cart, name='product_cart'),
    path('user/cart/add/<int:pk>/', views.product_cart_add, name='product_cart_add'),
    path('user/cart/remove/<int:pk>/', views.product_cart_remove, name='product_cart_remove'),
    path('product/quantity/<int:pk>/', views.update_product_quantity, name='update_product_quantity'),

    #Order
    path('user/checkout/', views.product_checkout, name='product_checkout'),
    path('user/order/cash-on-delivery/', views.product_order_cod, name='product_order_cod'),
    path('user/order/digital/', views.product_order_digital, name='product_order_digital'),
    path('user/order/wallet/', views.product_order_wallet, name='product_order_wallet'),

    #discount
    path('user/discount/', views.product_discount, name='product_discount'),

    #payment
    path('user/create-payment/', views.create_payment, name='create_payment'),
    path('user/payment/verify/', views.payment_verify, name='payment_verify'),
]