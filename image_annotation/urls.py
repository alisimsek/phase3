from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'image_annotation'

urlpatterns = [
    # /music/
    path('', views.index, name='index'),
    path('sign_in/', views.signin, name='signin'),
    path('sign_up/', views.signup, name='signup'),
    path('pwd_confirmation/', views.confirmation, name='confirmation')
]
