from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib.auth.models import User, Group
from django.conf import settings
from PIL import Image
from .forms import  UserForm, ImageUploadForm
from .models import *
from .image_list import *
import ast

# Create your views here.
def home_page(request):
    return render(request, 'image_annotation/home_page.html')

def main_page(request):
    imList = imageList()
    return render(request, 'image_annotation/image_list.html', {"imList" : imList})

def create_image(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        defaultAction = "ALLOW"
        image = LabeledImage(name=image_name,owner=request.user,action=defaultAction)
        image.save()
        return render(request, 'image_annotation/main_page.html', {"image_name" : image_name})

def load_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_name = request.POST['image_name']
            img = LabeledImage.objects.get(name=image_name)
            img.image = form.cleaned_data['image']
            img.save()
            return render(request, 'image_annotation/main_page.html', {"image_name" : image_name})


def add_rule(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        username = request.POST['username']
        shape = request.POST['shape']
        action = request.POST['action']
        rule_pos = request.POST['rule_pos']
        print(image_name)
        image = LabeledImage.objects.get(name=image_name)
        if request.user.username ==  image.owner.username:
            if type(rule_pos) == str:
                image.addRule(username, shape, action)
            else:
                image.addRule(username, shape, action, rule_pos)
            image.save()
            return render(request, 'image_annotation/main_page.html',{"image_name" : image_name})
        else:
            return render(request, 'image_annotation/not_authorized.html',{"image_name" : image_name})




def get_image(request):
    if request.method == "POST":
        if request.POST['username'] == request.user.username: # Now user can edit the image, addrules etc.
            image_name = request.POST['image_name']
            return render(request, 'image_annotation/main_page.html', {"image_name" : image_name})
        else: # Now user only can get the Image
            image_name = request.POST['image_name']
            image = LabeledImage.objects.get(name=image_name)
            img = image.getImage(request.user.username)
            w, h = img.size
            username = request.user.username
            print(username)
            img.save(settings.BASE_DIR + settings.STATIC_URL + "images/" + username + ".png")
            #return render(request, 'image_annotation/render_image.html')
            return render(request, 'image_annotation/render_image.html', {"w" : w, "h" : h, "username" : username})

def get_owner_image(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        image = LabeledImage.objects.get(name=image_name)
        img = image.getImage(request.user.username)
        w, h = img.size
        username = request.user.username
        print(username)
        img.save(settings.BASE_DIR + settings.STATIC_URL + "images/" + username + ".png")
        return render(request, 'image_annotation/render_image.html', {"w" : w, "h" : h, "username" : username})

def set_default(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        image = LabeledImage.objects.get(name=image_name)
        if request.user.username == image.owner.username:
            image.action = request.POST['action']
            image.save()
            return render(request, 'image_annotation/main_page.html',{"image_name" : image_name})
        else:
            return render(request, 'image_annotation/not_authorized.html',{"image_name" : image_name})

def del_rule(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        image = LabeledImage.objects.get(name=image_name)
        if request.user.username == image.owner.username:
            pos = request.POST['rule_pos']
            image.delRule(pos)
            image.save()
            return render(request, 'image_annotation/main_page.html',{"image_name" : image_name})
        else:
            return render(request, 'image_annotation/not_authorized.html',{"image_name" : image_name})

def usergroups(request):
    if request.method == "POST":
        groups = list(Group.objects.all())
        users = list(User.objects.all())
        if request.user.is_superuser:
            return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})
        else :
            return render(request, "image_annotation/user_groups.html", {"users":users, "groups":groups})

def add_user(request):
    if request.method == "POST":
        username = request.POST['username']
        groups = request.POST['groups']
        password = request.POST['password']

        usr = User(username=username)
        usr.set_password(password)
        usr.save()

        groups = ast.literal_eval(groups)
        for group in groups:
            try:
                Group.objects.get(name=group)
            except:
                Group.objects.create(name=group)
            gr = Group.objects.get(name=group)
            gr.user_set.add(usr)

        groups = list(Group.objects.all())
        users = list(User.objects.all())
        return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})

def add_group(request):
    if request.method == "POST":
        groupname = request.POST['groupname']
        try:
            Group.objects.get(name=groupname)
        except:
            Group.objects.create(name=groupname)

        groups = list(Group.objects.all())
        users = list(User.objects.all())
        return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})

def del_user(request):
    if request.method == "POST":
        username = request.POST['username']
        try:
            User.objects.get(username=username).delete()
        except:
            pass

        groups = list(Group.objects.all())
        users = list(User.objects.all())
        return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})

def del_group(request):
    if request.method == "POST":
        groupname = request.POST['groupname']
        try:
            Group.objects.get(name=groupname).delete()
        except:
            pass

        groups = list(Group.objects.all())
        users = list(User.objects.all())
        return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})

def get_groups(request):
    if request.method == "POST":
        username = request.POST['username']
        usr = User.objects.get(username=username)
        groups = list(usr.groups.all())
        return render(request, "image_annotation/show_groups.html", {"groups" : groups})

def get_users(request):
    if request.method == "POST":
        groupname = request.POST['groupname']
        group = Group.objects.get(name=groupname)
        users = list(group.user_set.all())
        return render(request, "image_annotation/show_users.html", {"users" : users})
def set_password(request):
    if request.method == "POST":
        if request.user.is_superuser:
            username = request.POST['username']
        else:
            username = request.user.username
        password = request.POST['password']

        usr = User.objects.get(username=username)
        usr.set_password(password)
        usr.save()

        groups = list(Group.objects.all())
        users = list(User.objects.all())
        if request.user.is_superuser:
            return render(request, "image_annotation/superuser.html", {"users":users, "groups":groups})
        else:
            return render(request, "image_annotation/user_groups.html", {"users":users, "groups":groups})

def is_member(request):
    if request.method == "POST":
        username = request.POST['username']
        groupname = request.POST['groupname']

        usr = User.objects.get(username=username)
        val = usr.groups.filter(name=groupname).exists()
        return render(request, "image_annotation/is_member.html", {"val":val})

def log_out(request):
    logout(request)
    return redirect('/')


class UserRegister(View):
    form_class = UserForm
    template_name = 'image_annotation/registration_form.html'

    # display a blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form' : form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            return redirect('/login')

        return render(request, self.template_name , {'form' : form})
