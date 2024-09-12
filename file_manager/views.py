# Create your views here.
from django.shortcuts import render, redirect
from .forms import PublicFileForm, PrivateFileForm

def upload_public_file(request):
    if request.method == 'POST':
        form = PublicFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_public_file')
    else:
        form = PublicFileForm()
    return render(request, 'file_manager/upload_public_file.html', {'form': form})


def upload_private_file(request):
    if request.method == 'POST':
        form = PrivateFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_private_file')
    else:
        form = PrivateFileForm()
    return render(request, 'file_manager/upload_private_file.html', {'form': form})