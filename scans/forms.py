from django.forms import ModelForm, TextInput
from django.contrib.auth.models import User
from django import forms
from .models import Collection
from .models import Filexml

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description',]
        widgets = {
                'name': TextInput(attrs={'class':'form-control'}),
                'description': TextInput(attrs={'class':'form-control'}),
                }

class UploadFile(forms.ModelForm):
    class Meta:
        model = Filexml
        fields = ['file_xml',]


class toRegister(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name','last_name']

