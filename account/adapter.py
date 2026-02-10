"""
Custom Allauth Adapter for the Account model.

This adapter customizes how django-allauth handles user creation
and authentication with our custom Account model.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


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
        
        This is a good place to connect social accounts to existing users
        if the email matches.
        """
        # If user exists with the same email, connect the social account
        if sociallogin.is_existing:
            return
        
        # Try to find an existing user by email
        email = sociallogin.account.extra_data.get('email')
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
            # For Twitter
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
