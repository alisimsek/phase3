from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'image_annotation'

urlpatterns = [
    # /music/
    path('', views.index, name='index'),
]
