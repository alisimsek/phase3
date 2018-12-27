from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from PIL import Image
from .forms import  UserForm
from .models import *
#from .phase1 import *



# Create your views here.
def home_page(request):
    return render(request, 'image_annotation/home_page.html', {"current_name" : "ali"})

def main_page(request):
    return render(request, 'image_annotation/main_page.html')

def create_image(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        defaultAction = "ALLOW"
        image = LabeledImage(name=image_name,ownr=request.user,action=defaultAction)
        image.create(request.user)
        image.save()
        return render(request, 'image_annotation/main_page.html')

def load_image(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        path = request.POST['image_path']
        image = LabeledImage.objects.get(name=image_name)
        image.create(request.user)
        image.loadImage(path)
        image.save()
        return render(request, 'image_annotation/main_page.html')

def add_rule(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        username = request.POST['username']
        shape = request.POST['shape']
        action = request.POST['action']
        rule_pos = request.POST['rule_pos']
        print(rule_pos)
        if rule_pos == None:
            rule_pos = "-1"
        image = LabeledImage.objects.get(name=image_name)
        image.create(request.user)
        image.addRule(username, shape, action, rule_pos)
        image.save()
        return render(request, 'image_annotation/main_page.html')

def get_image(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        image = LabeledImage.objects.get(name=image_name)
        image.create(request.user)
        img = image.getImage(request.user.username)
        print(img)
        print(img.size)
        img.save("saved.jpg")
        #return render(request, 'image_annotation/main_page.html')
        return render(request, 'image_annotation/render_image.html', {"img" : img})




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
