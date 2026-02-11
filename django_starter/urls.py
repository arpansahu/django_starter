from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

# DRF Spectacular for Swagger/OpenAPI
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from user_account.views import (
    CustomPasswordResetView,
    LogoutView,
    LoginView,
    AccountView,
    RegistrationView,
    activate,
    DeleteAccountView,
    DataDeletionCallbackView,
    SocialDisconnectView,
    test_notification,
)

from .views import (
     HomeView,
     start_task,
     trigger_demo_task,
     PrivacyPolicyView,
     TermsOfServiceView,
)

from file_manager.views import (
     upload_public_file,
     upload_protected_file,
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

    # Legal Pages (publicly accessible)
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
    
    # Facebook Data Deletion Callback (required for Facebook apps)
    path('data-deletion-callback/', DataDeletionCallbackView.as_view(), name='data_deletion_callback'),

    # Redirect allauth login to custom login page (must be BEFORE allauth.urls)
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('accounts/logout/', RedirectView.as_view(pattern_name='logout', permanent=False)),

    # Social Authentication (django-allauth) - Keep for OAuth callbacks
    path('accounts/', include('allauth.urls')),
    
    path('', HomeView.as_view(), name='home'),

    # file manager views
    path('upload-public/', upload_public_file, name='upload_public_file'),
    path('upload-protected/', upload_protected_file, name='upload_protected_file'),
    path('upload-private/', upload_private_file, name='upload_private_file'),
    
    # RabbitMQ messaging system
    path('messaging/', include('messaging_system.urls')),
    
    # Kafka event streaming
    path('events/', include('event_streaming.urls')),
    
    # Notes App - Django Generic Views Demo
    path('notes/', include('notes_app.urls', namespace='notes_app')),
    
    # Commands App - Management Commands Demo
    path('commands/', include('commands_app.urls', namespace='commands_app')),
    
    # Elasticsearch App - Search Demo
    path('elasticsearch/', include('elasticsearch_app.urls', namespace='elasticsearch_app')),
    
    # API App - Django REST Framework Demo
    path('api/v1/', include('api_app.urls', namespace='api_app')),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Django Progress Bar View
    path('start-task/', start_task, name='start-task'),
    path('trigger-demo-task/', trigger_demo_task, name='trigger_demo_task'),

    path('register/', RegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('account/', AccountView.as_view(), name='account'),
    path('account/delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('account/social/disconnect/<str:provider_id>/', SocialDisconnectView.as_view(), name='social_disconnect'),
    path('notifications/test/', test_notification, name='test_notification'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/', 
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

handler404 = 'user_account.views.error_404'
handler500 = 'user_account.views.error_500'
handler403 = 'user_account.views.error_403'
handler400 = 'user_account.views.error_400'