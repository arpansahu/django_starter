# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PublicFileForm, ProtectedFileForm, PrivateFileForm
from .models import PublicFile, ProtectedFile, PrivateFile

def upload_public_file(request):
    if request.method == 'POST':
        form = PublicFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save()
            messages.success(request, f'File "{file_instance.title}" uploaded successfully!')
            return redirect('upload_public_file')
        else:
            messages.error(request, 'Failed to upload file. Please check the form and try again.')
    else:
        form = PublicFileForm()
    
    # Get all uploaded public files
    files = PublicFile.objects.all().order_by('-id')
    return render(request, 'file_manager/public_form.html', {'form': form, 'files': files})


@login_required
def upload_protected_file(request):
    if request.method == 'POST':
        form = ProtectedFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.uploaded_by = request.user
            file_instance.save()
            messages.success(request, f'Protected file "{file_instance.title}" uploaded successfully!')
            return redirect('upload_protected_file')
        else:
            messages.error(request, 'Failed to upload file. Please check the form and try again.')
    else:
        form = ProtectedFileForm()
    
    # Get all uploaded protected files
    files = ProtectedFile.objects.all().order_by('-id')
    return render(request, 'file_manager/protected_form.html', {'form': form, 'files': files})


def upload_private_file(request):
    if request.method == 'POST':
        form = PrivateFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save()
            messages.success(request, f'File "{file_instance.title}" uploaded successfully!')
            return redirect('upload_private_file')
        else:
            messages.error(request, 'Failed to upload file. Please check the form and try again.')
    else:
        form = PrivateFileForm()
    
    # Get all uploaded private files
    files = PrivateFile.objects.all().order_by('-id')
    return render(request, 'file_manager/upload_private_file.html', {'form': form, 'files': files})

    