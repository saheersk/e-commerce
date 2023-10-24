from user.models import Wallet

def wallet(request):
    if request.user.is_authenticated:
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            wallet = 0
            return {'wallet_amount': wallet}

        return {'wallet_amount': wallet.balance}
    else:
        return {'wallet_amount': 0}
    
