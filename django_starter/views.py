from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .tasks import long_running_task, demo_task

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class HomeView(View):
    def get(self, request, *args, **kwargs):
        context ={}
        return render(self.request, template_name='Home.html', context=context)

def start_task(request):
    task = long_running_task.delay()
    return JsonResponse({'task_id': task.id})

def trigger_demo_task(request):
    task = demo_task.delay()  # Trigger the Celery task asynchronously
    return JsonResponse({'task_id': task.id, 'status': 'Task has been triggered'})


class PrivacyPolicyView(TemplateView):
    """Privacy Policy page - publicly accessible"""
    template_name = 'legal/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    """Terms of Service page - publicly accessible"""
    template_name = 'legal/terms_of_service.html'