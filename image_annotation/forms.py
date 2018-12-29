from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        help_texts = {'username':None,}
        fields = ['username', 'password']

class ImageUploadForm(forms.Form):
    image = forms.ImageField()
