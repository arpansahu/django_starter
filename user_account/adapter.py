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

logger = logging.getLogger(__name__)


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
