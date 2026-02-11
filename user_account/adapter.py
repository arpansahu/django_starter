"""
Custom Allauth Adapter for the Account model.

This adapter customizes how django-allauth handles user creation
and authentication with our custom Account model.
"""
import logging
import traceback

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.template.loader import render_to_string
from mailjet_rest import Client

from user_account.notifications import notify_user

logger = logging.getLogger(__name__)


def _get_provider_display_name(sociallogin):
    """Get a human-readable provider name from a sociallogin."""
    provider_id = sociallogin.account.provider
    name_map = {
        'google': 'Google',
        'github': 'GitHub',
        'facebook': 'Facebook',
        'twitter_oauth2': 'X (Twitter)',
        'linkedin': 'LinkedIn',
    }
    return name_map.get(provider_id, provider_id.title())


def _send_mailjet_email(to_email, to_name, subject, text_body, html_body):
    """Send an email via Mailjet REST API."""
    mailjet = Client(
        auth=(settings.MAIL_JET_API_KEY, settings.MAIL_JET_API_SECRET),
        version='v3.1',
    )
    data = {
        'Messages': [{
            "From": {
                "Email": settings.DEFAULT_FROM_EMAIL,
                "Name": "Django Starter",
            },
            "To": [{
                "Email": to_email,
                "Name": to_name,
            }],
            "Subject": subject,
            "TextPart": text_body,
            "HTMLPart": html_body,
            "CustomID": to_email,
        }]
    }
    result = mailjet.send.create(data=data)
    logger.info("Mailjet send result for %s: %s", to_email, result.status_code)
    return result


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for regular (non-social) account operations.
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new User instance using information provided in the signup form.
        """
        user = super().save_user(request, user, form, commit=False)
        # Custom fields can be set here if needed
        if commit:
            user.save()
        return user
    
    def get_login_redirect_url(self, request):
        """
        Returns the URL to redirect to after a successful login.
        """
        return settings.LOGIN_REDIRECT_URL
    
    def get_logout_redirect_url(self, request):
        """
        Returns the URL to redirect to after logout.
        """
        return settings.LOGOUT_REDIRECT_URL


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account operations.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        
        This connects social accounts to existing users if the email matches.
        """
        # If user exists with the same email, connect the social account
        if sociallogin.is_existing:
            return
        
        # Try to find an existing user by email from multiple sources
        email = None
        
        # Source 1: extra_data (Google, GitHub, Facebook, etc.)
        email = sociallogin.account.extra_data.get('email')
        
        # Source 2: email_addresses from allauth (covers all providers)
        if not email and sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
        
        # Source 3: user object populated by allauth
        if not email and sociallogin.user and sociallogin.user.email:
            email = sociallogin.user.email
        
        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
                # Send connected notification email
                provider_name = _get_provider_display_name(sociallogin)
                try:
                    ctx = {
                        'user': user,
                        'provider': provider_name,
                        'domain': settings.DOMAIN,
                        'protocol': settings.PROTOCOL,
                    }
                    text_body = (
                        f"Hi {user.username},\n\n"
                        f"Your {provider_name} account has been connected to your Django Starter account.\n"
                        f"You can now sign in using {provider_name}.\n\n"
                        f"If you did not do this, please secure your account immediately.\n\n"
                        f"— Django Starter Team"
                    )
                    html_body = render_to_string('email/social_connected.html', ctx)
                    _send_mailjet_email(
                        user.email, user.username,
                        f'[Django Starter] {provider_name} Account Connected',
                        text_body, html_body,
                    )
                except Exception as e:
                    logger.exception("Failed to send social connected email to %s", user.email)
                # Real-time WebSocket notification
                try:
                    notify_user(
                        user.id,
                        f'{provider_name} Connected',
                        f'Your {provider_name} account has been linked to your Django Starter account.',
                        level='success',
                    )
                except Exception as e:
                    logger.debug("WS connected notification skipped (channel layer unavailable): %s", e)
            except User.DoesNotExist:
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login user.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Activate user immediately for social logins
        user.is_active = True
        user.save()
        
        # Send welcome email for first-time social signup
        provider_name = _get_provider_display_name(sociallogin)
        if user.email:
            try:
                ctx = {
                    'user': user,
                    'provider': provider_name,
                    'domain': settings.DOMAIN,
                    'protocol': settings.PROTOCOL,
                }
                text_body = (
                    f"Hi {user.username},\n\n"
                    f"Welcome to Django Starter! Your account has been created using {provider_name}.\n\n"
                    f"Username: {user.username}\n"
                    f"Email: {user.email}\n"
                    f"Signed up via: {provider_name}\n\n"
                    f"You can now explore all features. Visit your account page to manage your profile.\n\n"
                    f"— Django Starter Team"
                )
                html_body = render_to_string('email/welcome_social.html', ctx)
                _send_mailjet_email(
                    user.email, user.username,
                    f'[Django Starter] Welcome, {user.username}!',
                    text_body, html_body,
                )
            except Exception as e:
                logger.exception("Failed to send welcome email to %s", user.email)
            # Real-time WebSocket notification
            try:
                notify_user(
                    user.id,
                    'Welcome!',
                    f'Your account has been created via {provider_name}. Explore all features!',
                    level='success',
                )
            except Exception as e:
                logger.debug("WS welcome notification skipped (channel layer unavailable): %s", e)
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Extract additional data from social profile if available
        extra_data = sociallogin.account.extra_data
        
        # Generate username if not provided
        if not user.username:
            # Try different sources for username
            username = None
            
            # For GitHub
            if 'login' in extra_data:
                username = extra_data.get('login', '')
            # For Google/Facebook - use part of email
            elif user.email:
                username = user.email.split('@')[0]
            # For Twitter OAuth 2.0
            elif 'username' in extra_data:
                username = extra_data.get('username', '')
            # For Twitter OAuth 1.0a (legacy)
            elif 'screen_name' in extra_data:
                username = extra_data.get('screen_name', '')
            # For LinkedIn
            elif 'localizedFirstName' in extra_data and 'localizedLastName' in extra_data:
                username = f"{extra_data.get('localizedFirstName', '')}_{extra_data.get('localizedLastName', '')}".lower()
            
            # Ensure username is unique
            if username:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                base_username = username[:30]  # Account model has max_length=30
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username[:27]}_{counter}"  # Leave room for counter
                    counter += 1
                
                user.username = username
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the URL to redirect to after successfully connecting a social account.
        """
        return settings.LOGIN_REDIRECT_URL

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        """
        Called when social authentication fails. Logs the full error details
        so we can debug "Third-Party Login Failure" errors.
        """
        provider_id = getattr(provider, 'id', provider)
        logger.error(
            "Social auth error for provider '%s': error=%s, exception=%s",
            provider_id, error, exception,
        )
        if exception:
            logger.error(
                "Social auth exception traceback:\n%s",
                traceback.format_exception(type(exception), exception, exception.__traceback__),
            )
        if extra_context:
            logger.error("Social auth extra_context: %s", extra_context)
        super().on_authentication_error(request, provider, error, exception, extra_context)
