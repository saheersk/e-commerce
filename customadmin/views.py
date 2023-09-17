from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from customadmin.forms import AdminCustomUserForm, AdminCustomUpdateUserForm, AdminCategory
from user.models import CustomUser
from user.functions import generate_form_error
from shop.models import Category


#Admin User
@login_required(login_url="admin-login/")
def admin_panel(request):
    context = {
        "title": "Male Fashion | Admin Panel",
        "username": request.user.username if request.user.is_authenticated else None,
    }
    return render(request, 'customadmin/admin-panel.html', context)


def admin_login(request):
    context = {
        "title": "Male Fashion | Admin Login",
    }
    return render(request, 'customadmin/admin-login.html', context)


def admin_logout(request):
    auth_logout(request)
    return redirect('customadmin:admin_login')


@login_required(login_url="admin-login/")
def admin_user(request):
    users = CustomUser.objects.all()

    context = {
        "title": "Male Fashion | Admin User",
        'users': users,
        'heading': ['First Name', 'Last Name', 'Email', 'Phone Number', 'Superuser']
    }
    return render(request, 'customadmin/admin-table-user.html', context)


@login_required(login_url="admin-login/")
def admin_user_add(request):
    if request.method == 'POST':
        form = AdminCustomUserForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            is_superuser = form.cleaned_data.get('is_superuser')

            staff = False
            super_user = False

            if is_superuser:
                super_user = True
                staff = True

            CustomUser.objects.create_user(
                    username=instance.first_name,
                    password=instance.password,
                    email=instance.email,
                    first_name=instance.first_name,
                    last_name = instance.last_name,
                    is_staff=super_user,
                    is_superuser=staff
            )

            return HttpResponseRedirect(reverse("customadmin:admin_user"))
        else:
            message = generate_form_error(form)
            form = AdminCustomUserForm()
            context = {
                "title": "Male Fashion | Admin Add",
                "error" : True,
                "message" : message,
                "form": form,
            }
        return render(request, 'customadmin/admin-add.html', context=context)
    else:
        form = AdminCustomUserForm()
        context = {
            "title": "Male Fashion | Admin Add",
            "user_tag": "User",
            "form": form
        }
        return render(request, 'customadmin/admin-add.html', context)


@login_required(login_url="admin-login/")
def admin_user_edit(request, pk):
    user = get_object_or_404(CustomUser, id=pk)

    if request.method == 'POST':
        form = AdminCustomUpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            is_superuser = form.cleaned_data.get('is_superuser')

            user.is_superuser = is_superuser
            user.is_staff = is_superuser

            form.save()
            return redirect('customadmin:admin_user')
        else:
            message = generate_form_error(form)
            context = {
                "title": "Male Fashion | Admin Edit",
                "error" : True,
                "message" : message,
                "form": form,
                "user": user,
            }
        return render(request, 'customadmin/admin-edit.html', context)
    else:
        form = AdminCustomUpdateUserForm(instance=user)
        
        context = {
            "title": "Male Fashion | Admin Edit",
            "user": user,
            "form": form,
        }
        return render(request, 'customadmin/admin-edit.html', context)
    

@login_required(login_url="admin-login/")
def admin_user_delete(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    user.delete()
    return HttpResponse("User deleted successfully")


#Admin Category
@login_required(login_url="admin-login/")
def admin_category(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'heading': ['Name']
    }
    return render(request, 'customadmin/admin-table-category.html', context)


@login_required(login_url="admin-login/")
def admin_category_add(request):
    if request.method == 'POST':
        form = AdminCategory(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            Category.objects.create(name=instance.name)

            return HttpResponseRedirect(reverse("customadmin:admin_category"))
    else:
        form = AdminCategory()
        context = {
            "form": form,
        }
        return render(request, 'customadmin/admin-add.html', context)


@login_required(login_url="admin-login/")
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        form = AdminCategory(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("customadmin:admin_category"))
    else:
        form = AdminCategory(instance=category)
        context = {
            "form": form,
        }
        return render(request, 'customadmin/admin-add.html', context)


@login_required(login_url="admin-login/")
def admin_category_delete(request, pk):
    pass