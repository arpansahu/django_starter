from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class HomeView(View):
    def get(self, request, *args, **kwargs):
        context ={}
        return render(self.request, template_name='Home.html', context=context)

