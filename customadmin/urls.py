from django.urls import path
from customadmin import views


app_name = "customadmin"


urlpatterns = [
    # Home
    path('', views.admin_panel, name='admin_panel'),

    # Admin Login
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # Authentication Details
    path('user/users/', views.admin_user, name='admin_user'),
    path('user/users/add/', views.admin_user_add, name='admin_user_add'),
    path(
        'user/users/edit/<int:pk>/',
        views.admin_user_edit,
        name='admin_user_edit'),
    path(
        'user/users/delete/<int:pk>/',
        views.admin_user_delete,
        name='admin_user_delete'),
    path(
        'user/users/block/<int:pk>/',
        views.admin_user_block,
        name='admin_user_block'),

    # Admin Category
    path('category/categories/', views.admin_category, name='admin_category'),
    path(
        'category/categories/add/',
        views.admin_category_add,
        name='admin_category_add'),
    path(
        'category/categories/edit/<int:pk>/',
        views.admin_category_edit,
        name='admin_category_edit'),
    path(
        'category/categories/delete/<int:pk>/',
        views.admin_category_delete,
        name='admin_category_delete'),

    # Discount Coupon
    path('coupon/coupons/', views.admin_coupon, name='admin_coupon'),
    path(
        'coupon/coupons/add/',
        views.admin_coupon_add,
        name='admin_coupon_add'),
    path(
        'coupon/coupons/edit/<int:pk>/',
        views.admin_coupon_edit,
        name='admin_coupon_edit'),
    #Category Offer
    path('category/offer/', views.admin_category_offer, name='admin_category_offer'),
    path(
        'category/offer/add/',
        views.admin_category_offer_add,
        name='admin_category_offer_add'),
    path(
        'category/offer/edit/<int:pk>/',
        views.admin_category_offer_edit,
        name='admin_category_offer_edit'),
    #Product Offer
    path('product/offer/', views.admin_product_offer, name='admin_product_offer'),
    path(
        'product/offer/add/',
        views.admin_product_offer_add,
        name='admin_product_offer_add'),
    path(
        'product/offer/edit/<int:pk>/',
        views.admin_product_offer_edit,
        name='admin_product_offer_edit'),
    #Referral
    path('user/referral/offer/', views.admin_referral_offer, name='admin_referral_offer'),
    path(
        'user/referral/offer/edit/',
        views.admin_referral_offer_edit,
        name='admin_referral_offer_edit'),


    # Admin Product
    path('product/products/', views.admin_product, name='admin_product'),
    path(
        'product/products/add/',
        views.admin_product_add,
        name='admin_product_add'),
    path(
        'product/products/edit/<int:pk>/',
        views.admin_product_edit,
        name='admin_product_edit'),
    path(
        'product/products/delete/<int:pk>/',
        views.admin_product_delete,
        name='admin_product_delete'),
    # Product Variant
    path(
        'product/variant/',
        views.admin_product_variant,
        name='admin_product_variant'),
    path(
        'product/variant/add/',
        views.admin_product_variant_add,
        name='admin_product_variant_add'),
    path('product/variant/edit/<int:pk>/',
         views.admin_product_variant_edit,
         name='admin_product_variant_edit'),
    path('product/variant/delete/<int:pk>/',
         views.admin_product_variant_delete,
         name='admin_product_variant_delete'),

    # Order
    path('order/orders/', views.admin_order, name='admin_order'),
    path('order/orders/<int:pk>/', views.admin_order_details, name='admin_order_details'),
    path(
        'order/orders/edit/<int:pk>/',
        views.admin_order_edit,
        name='admin_order_edit'),
    path(
        'order/orders-cancelled-or-returned/',
        views.admin_order_center,
        name='admin_order_center'),
    path('order/orders-cancelled-or-returned/edit/<int:pk>/',
         views.admin_order_center_edit, name='admin_order_center_edit'),
    path('order/orders-cancelled-or-returned/approve/<int:pk>/',
         views.admin_order_center_approve, name='admin_order_center_approve'),
    path(
        'order/orders-cancelled-or-returned/completed/<int:pk>/',
        views.admin_order_center_completed,
        name='admin_order_center_completed'),

    # sales
    path(
        'order/orders/sales-report/',
        views.admin_sales_report,
        name='admin_sales_report'),
    path(
        'order/orders/sales-report/download_csv/',
        views.download_sales_report_csv,
        name='download_sales_report_csv'),
    #Reviews
    path('order/reviews/', views.admin_reviews, name='admin_reviews'),
    path('order/reviews/reply/<int:pk>/', views.admin_review_reply, name='admin_review_reply'),

    # Contact
    path('contact/details/', views.admin_contact, name='admin_contact'),

    # Banner
    path('banner/details/', views.admin_banner, name='admin_banner'),
    path(
        'banner/details/add/',
        views.admin_banner_add,
        name='admin_banner_add'),
    path(
        'banner/details/edit/<int:pk>/',
        views.admin_banner_edit,
        name='admin_banner_edit'),
    path(
        'banner/details/delete/<int:pk>/',
        views.admin_banner_delete,
        name='admin_banner_delete'),

    #Notification
    path(
        'notification/broadcast/',
        views.admin_notification,
        name='admin_notification'),
    path(
        'notification/broadcast/add/',
        views.admin_notification_add,
        name='admin_notification_add'),
    path(
        'notification/broadcast/edit/<int:pk>/',
        views.admin_notification_edit,
        name='admin_notification_edit'),
]
