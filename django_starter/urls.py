from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from account.views import (
    CustomPasswordResetView,
    LogoutView,
    LoginView,
    AccountView,
    RegistrationView,
    activate,
)

from .views import (
     HomeView,
     start_task,
     trigger_demo_task,
)

from file_manager.views import (
     upload_public_file,
     upload_private_file,
)

def trigger_error(request):
    division_by_zero = 1 / 0

def large_resource(request):
   time.sleep(4)
   return HttpResponse("Done!")

urlpatterns = [
    # Admin URL
     path('django-admin/', admin.site.urls, name='admin'),

    path('', HomeView.as_view(), name='home'),

    # file manager views
    path('upload-public/', upload_public_file, name='upload_public_file'),
    path('upload-private/', upload_private_file, name='upload_private_file'),

    # Django Progress Bar View
    path('start-task/', start_task, name='start-task'),
    path('trigger-demo-task/', trigger_demo_task, name='trigger_demo_task'),

    path('register/', RegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('account/', AccountView.as_view(), name='account'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         activate, name='account_activate'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'),
         name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_change.html'),
         name='password_reset_confirm'),

    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    #sentry test view 
    path('sentry-debug/', trigger_error),
    path('large_resource/', large_resource)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'account.views.error_404'
handler500 = 'account.views.error_500'
handler403 = 'account.views.error_403'
handler400 = 'account.views.error_400'