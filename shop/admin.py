from django.contrib import admin

from shop.models import Category, ProductImage, Product, Cart, Order, OrderStatus, Payment, PaymentMethod, ProductSize


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    extra = 5 
    max_num = 5 


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(Category, CategoryAdmin)


class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'stock_unit']

admin.site.register(ProductSize, ProductSizeAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'is_show', 'size']
    inlines = [ProductImageAdmin]

admin.site.register(Product, ProductAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'qty']

admin.site.register(Cart, CartAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_status']

admin.site.register(Order, OrderAdmin)


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']

admin.site.register(OrderStatus, OrderStatusAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_method', 'transaction_id', 'purchased_price']

admin.site.register(Payment, PaymentAdmin)


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_type']

admin.site.register(PaymentMethod, PaymentMethodAdmin)