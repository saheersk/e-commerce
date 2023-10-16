
def username(request):
    if request.user.is_authenticated:
        return {'username': request.user.first_name + ' ' + request.user.last_name }
    else:
        return {'username': None}
