from user.models import Wallet

def wallet(request):
    if request.user.is_authenticated:
        wallet =  Wallet.objects.get(user=request.user)
        return {'wallet_amount': wallet.balance}
    else:
        return {'wallet_amount': 0}