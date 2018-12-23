from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, 'image_annotation/home_page.html', {"current_name" : "ali"})

def signin(request):
    return render(request, 'image_annotation/sign_in.html')

def signup(request):
    return render(request, 'image_annotation/sign_up.html')

def confirmation(request):
    if request.method == 'POST':
        username = request.POST["Username"]
        return HttpResponse(username)
    return render(request, 'image_annotation/confirmation.html')
