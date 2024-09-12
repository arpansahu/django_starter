# file_manager/forms.py
from django import forms
from .models import PublicFile, PrivateFile

class PublicFileForm(forms.ModelForm):
    class Meta:
        model = PublicFile
        fields = ['title', 'file']

class PrivateFileForm(forms.ModelForm):
    class Meta:
        model = PrivateFile
        fields = ['title', 'file']
