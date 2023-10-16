from django.urls import path
from django.conf.urls import handler404

from web import views

app_name = "web"


urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]

handler404 = views.custom_404_view