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
    path('create_image/', views.create_image, name='create_image'),
    path('load_image/', views.load_image, name='load_image'),
    path('add_rule/', views.add_rule, name='add_rule'),
    path('get_image/', views.get_image, name='get_image'),
    path('get_owner_image/', views.get_owner_image, name='get_owner_image'),
    path('set_default/', views.set_default, name='set_default'),
    path('del_rule/', views.del_rule, name='del_rule'),
    path('usergroups/', views.usergroups, name='usergroups'),
    path('add_user/', views.add_user, name='add_user'),
    path('add_group/', views.add_group, name='add_group'),
    path('del_user/', views.del_user, name='del_user'),
    path('del_group/', views.del_group, name='del_group'),
    path('get_groups/', views.get_groups, name='get_groups'),
    path('get_users/', views.get_users, name='get_users'),
    path('set_password/', views.set_password, name='set_password'),
    path('is_member/', views.is_member, name='is_member'),
    path('log_out/', views.log_out, name='log_out'),
]
