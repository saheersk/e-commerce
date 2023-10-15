from django.urls import path
from web import views


app_name = "web"


urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('not-found/', views.custom_404_view, name='custom_404_view'),
]

handler404 = 'web.views.custom_404_view'