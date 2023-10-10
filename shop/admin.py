from django.contrib import admin

from shop.models import Category, ProductImage, Product, Cart, Order, OrderStatus, Payment, PaymentMethod, ProductVariant, OrderItem, OrderManagement, WalletHistory, UserReview, CategoryOffer, ProductOffer


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    extra = 5 
    max_num = 5 


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'is_show']
    inlines = [ProductImageAdmin]

admin.site.register(Product, ProductAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'qty']

admin.site.register(Cart, CartAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'order_status']

admin.site.register(OrderItem, OrderItemAdmin)


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']

admin.site.register(OrderStatus, OrderStatusAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_method', 'transaction_id', 'purchased_price']

admin.site.register(Payment, PaymentAdmin)


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_type']

admin.site.register(PaymentMethod, PaymentMethodAdmin)


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant_name','stock_unit', 'size']

admin.site.register(ProductVariant, ProductVariantAdmin)


class OrderManagementAdmin(admin.ModelAdmin):
    list_display = ['id', 'ordered_product', 'status']

admin.site.register(OrderManagement, OrderManagementAdmin)


class WalletHistoryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'transaction_operation']

admin.site.register(WalletHistory, WalletHistoryAdmin)



admin.site.register(UserReview)


admin.site.register(CategoryOffer)


admin.site.register(ProductOffer)