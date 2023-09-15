from django.urls import path
from web import views


app_name = "customadmin"


urlpatterns = [
    path('', views.index, name='index'),
]