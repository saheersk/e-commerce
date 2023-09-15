from django.contrib import admin

from shop.models import Category, ProductImage, Product


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    extra = 5 
    max_num = 5 


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'stock_unit', 'is_show']
    inlines = [ProductImageAdmin]

admin.site.register(Product, ProductAdmin)
