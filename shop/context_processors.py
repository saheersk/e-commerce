from shop.models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        return {'cart_count': request.session.get('cart_count', 0)}
    else:
        return {'cart_count': 0}
    
