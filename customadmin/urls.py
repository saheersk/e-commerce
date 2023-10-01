from django.urls import path
from customadmin import views


app_name = "customadmin"


urlpatterns = [
    #Home
    path('', views.admin_panel, name='admin_panel'),

    #Admin Login
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    #Authentication Details
    path('user/users/', views.admin_user, name='admin_user'),
    path('user/users/add/', views.admin_user_add, name='admin_user_add'),
    path('user/users/edit/<int:pk>/', views.admin_user_edit, name='admin_user_edit'),
    path('user/users/delete/<int:pk>/', views.admin_user_delete, name='admin_user_delete'),
    path('user/users/block/<int:pk>/', views.admin_user_block, name='admin_user_block'),

    #Admin Category
    path('category/categories/', views.admin_category, name='admin_category'),
    path('category/categories/add/', views.admin_category_add, name='admin_category_add'),
    path('category/categories/edit/<int:pk>/', views.admin_category_edit, name='admin_category_edit'),
    path('category/categories/delete/<int:pk>/', views.admin_category_delete, name='admin_category_delete'),

    #Admin Product
    path('product/products/', views.admin_product, name='admin_product'),
    path('product/products/add/', views.admin_product_add, name='admin_product_add'),
    path('product/products/edit/<int:pk>/', views.admin_product_edit, name='admin_product_edit'),
    path('product/products/delete/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),
    #Product Variant
    path('product/variant/', views.admin_product_variant, name='admin_product_variant'),
    path('product/variant/add/', views.admin_product_variant_add, name='admin_product_variant_add'),
    path('product/variant/edit/<int:pk>/', views.admin_product_variant_edit, name='admin_product_variant_edit'),
    path('product/variant/delete/<int:pk>/', views.admin_product_variant_delete, name='admin_product_variant_delete'),

    #Order
    path('order/orders/', views.admin_order, name='admin_order'),
    path('order/orders/edit/<int:pk>/', views.admin_order_edit, name='admin_order_edit'),

    #Contact
    path('contact/details/', views.admin_contact, name='admin_contact'),

    #Banner
    path('banner/details/', views.admin_banner, name='admin_banner'),
    path('banner/details/add/', views.admin_banner_add, name='admin_banner_add'),
    path('banner/details/edit/<int:pk>/', views.admin_banner_edit, name='admin_banner_edit'),
    path('banner/details/delete/<int:pk>/', views.admin_banner_delete, name='admin_banner_delete'),

]