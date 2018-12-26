from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


app_name = 'image_annotation'

urlpatterns = [
    # /music/
    path('', views.home_page, name='home_page'),
    path('sign_up/', views.UserRegister.as_view(), name='signup'),
    path('main_page/', views.main_page, name='main_page'),
    path('', include('django.contrib.auth.urls')),
]
