from django.shortcuts import render, get_object_or_404

from shop.models import Product, ProductImage


def product_all(request):
    products = Product.objects.filter(is_show=True)

    context = {
        'title': 'Male Fashion | Products',
        'products': products
    }
    return render(request, 'product/shop.html', context)


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_images = ProductImage.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    context = {
        'title': f'Male Fashion | {product.title}',
        'product': product,
        'product_images': product_images,
        'related_products': related_products
    }
    return render(request, 'product/shop-details.html', context)