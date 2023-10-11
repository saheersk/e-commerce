from django.apps import apps
from django.utils import timezone

from celery import shared_task


#Category Offer
def calculate_discount_price(product, offer):
    price = product.discount_amount
    if offer.discount_type == 'amount':
        price = product.price - offer.amount_or_percent
    elif offer.discount_type == 'percent':
        price = product.price - (product.price * offer.amount_or_percent / 100)
    
    return price


@shared_task
def apply_category_offers():
    today = timezone.localdate()
    i =0
    i+=1
    print(i, 'iii')
    CategoryOffer = apps.get_model('shop', 'CategoryOffer') 
    valid_offers = CategoryOffer.objects.filter(valid_from__lte=today, active=True)

    Product = apps.get_model('shop', 'Product') 

    for offer in valid_offers:
        products_in_category = Product.objects.filter(category=offer.category)

        for product in products_in_category:
            if offer.applied:
                if offer.valid_to.date() < today:
                    product.discount_amount = 0.00
                    offer.active=False

                    product.save()
                    offer.save()
                else:
                    price = calculate_discount_price(product, offer)
                    if price < product.discount_amount or product.discount_amount == 0:
                        product.discount_amount = price
                    product.save()
                continue
                 
            price = calculate_discount_price(product, offer)

            if price > product.discount_amount:
                product.discount_amount = price

            product.save()

        offer.applied=True
        offer.save()


#Product Offer
@shared_task
def apply_product_offers():
    today = timezone.localdate()

    ProductOffer = apps.get_model('shop', 'ProductOffer') 
    valid_offers = ProductOffer.objects.filter(valid_from__lte=today, active=True)
    print(valid_offers, 'valid')

    for offer in valid_offers:
        for product in offer.products.all():
            print(product.price, 'product')
            if offer.applied:
                if offer.valid_to.date() < today:
                    product.discount_amount = 0.00
                    offer.active = False

                    product.save()
                    offer.save()
                else:
                    price = calculate_discount_price(product, offer)
                    print(price, 'price')
                    if price < product.discount_amount or product.discount_amount == 0:
                        product.discount_amount = price
                    product.save()
                continue

            max_discount = product.discount_amount
            price = calculate_discount_price(product, offer)

            if price < product.discount_amount:
                product.discount_amount = price

            product.save()

        offer.applied = True
        offer.save()

    apply_category_offers()


    
