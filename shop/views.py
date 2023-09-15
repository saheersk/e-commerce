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

    context = {
        'title': f'Male Fashion | {product.title}',
        'products': product,
        'product_images': product_images,
    }
    return render(request, 'product/shop-details.html', context)