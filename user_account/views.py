import ssl

from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, RedirectView
from django.utils.translation import gettext_lazy as _

from user_account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, PasswordResetForm, LoginForm
from django.conf import settings
from django.contrib.auth.views import PasswordContextMixin

from user_account.models import Account
from user_account.token import account_activation_token

DOMAIN = settings.DOMAIN
PROTOCOL = settings.PROTOCOL

from mailjet_rest import Client

mailjet = Client(auth=(settings.MAIL_JET_API_KEY, settings.MAIL_JET_API_SECRET), version='v3.1')


# Create your views here.

class CustomPasswordResetView(PasswordContextMixin, FormView):
    email_template_name = "registration/password_reset_email.html"
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"
    title = _("Password reset")
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


def send_mail_account_activate(reciever_email, user, SUBJECT="[Django Starter] Confirm Your Email"):
    template_context = {
        'user': user,
        'protocol': PROTOCOL,
        'domain': DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    }
    text_part = render_to_string('account/activate_account_mail.html', template_context)
    html_part = render_to_string('email/activation.html', template_context)

    from_email = settings.DEFAULT_FROM_EMAIL
    data = {
        'Messages': [
            {
                "From": {
                    "Email": from_email,
                    "Name": "Django Starter"
                },
                "To": [
                    {
                        "Email": reciever_email,
                        "Name": user.username
                    }
                ],
                "Subject": SUBJECT,
                "TextPart": text_part,
                "HTMLPart": html_part,
                "CustomID": f"{reciever_email}"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print("account activation mail sent")
    return result


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'account/account_activation_done.html', context={'message': 'Thank you for your email '
                                                                                           'confirmation. Now you can '
                                                                                           'login your account.'})
    else:
        return render(request, 'account/account_activation_done.html', context={'message': 'Activation link is invalid!'})


class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        form = RegistrationForm()
        context['registration_form'] = form
        return render(request, 'account/register.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save()
            email = form.cleaned_data.get('email')
            send_mail_account_activate(email, account)
            return render(request, 'account/account_activation_done.html', {'message': 'Check your mail and activate your account'})
        else:
            context['registration_form'] = form
        return render(request, 'account/register.html', context)


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class LogoutView(RedirectView):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class LoginView(View):
    def get(self, request):
        form = LoginForm(request.POST or None)
        msg = None
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, "account/login.html", {"form": form, "msg": msg})

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(email=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

        return render(request, "account/login.html", {"form": form, "msg": msg})


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class AccountView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
            }
        )
        context['account_form'] = form
        return render(request, 'account/account.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

        context['account_form'] = form
        return render(request, 'account/account.html', context)


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class DeleteAccountView(View):
    """View for account deletion with confirmation"""
    
    def get(self, request, *args, **kwargs):
        """Show confirmation page before deletion"""
        return render(request, 'account/delete_account_confirm.html')
    
    def post(self, request, *args, **kwargs):
        """Handle account deletion"""
        user = request.user
        
        # Log user out before deletion
        logout(request)
        
        # Delete the user account
        user.delete()
        
        # Render success page
        return render(request, 'account/delete_account_done.html', {
            'message': 'Your account has been successfully deleted. We\'re sorry to see you go!'
        })

def error_404(request, exception):
    return render(request, 'error/error_404.html')


def error_400(request, exception):
    return render(request, 'error/error_400.html')


def error_403(request, exception):
    return render(request, 'error/error_403.html')


def error_500(request):
    return render(request, 'error/error_500.html')


class DataDeletionCallbackView(View):
    """Public view for Facebook Data Deletion Callback URL
    Required by Facebook Platform Policy for apps using Facebook Login.
    This page explains data deletion and provides a way for users to request deletion.
    """
    
    def get(self, request, *args, **kwargs):
        """Show data deletion information page"""
        return render(request, 'account/data_deletion_callback.html')
    
    def post(self, request, *args, **kwargs):
        """Handle data deletion request from the page"""
        email = request.POST.get('email', '')
        reason = request.POST.get('reason', '')
        
        context = {
            'email': email,
            'submitted': True,
            'message': 'Your data deletion request has been received. We will process it within 30 days as per our policy.'
        }
        
        # In production, you might want to:
        # 1. Send an email notification to admins
        # 2. Log the request in database
        # 3. Create a task to process the deletion
        
        return render(request, 'account/data_deletion_callback.html', context)