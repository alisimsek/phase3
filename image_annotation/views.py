from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import  UserForm



# Create your views here.
def home_page(request):
    return render(request, 'image_annotation/home_page.html', {"current_name" : "ali"})

def main_page(request):
    return render(request, 'image_annotation/confirmation.html')

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
