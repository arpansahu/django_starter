from django.apps import AppConfig
from django.conf import settings


class DjangoStarterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_starter'

    def ready(self):
        """
        Update Site domain on startup based on environment variables.
        This ensures OAuth callbacks work correctly in both dev and prod.
        """
        try:
            from django.contrib.sites.models import Site
            
            # Get domain from environment
            domain = settings.DOMAIN
            # Clean protocol - remove :// if present, we'll add it back
            protocol = settings.PROTOCOL.replace('://', '').replace('/', '')
            
            # Update Site domain
            site = Site.objects.get(id=settings.SITE_ID)
            if site.domain != domain:
                site.domain = domain
                site.name = f'Django Starter ({domain})'
                site.save()
                print(f"\n{'='*70}")
                print(f"✓ Site domain updated to: {domain}")
                print(f"✓ OAuth callback URLs for all providers:")
                print(f"  - Google:      {protocol}://{domain}/accounts/google/login/callback/")
                print(f"  - GitHub:      {protocol}://{domain}/accounts/github/login/callback/")
                print(f"  - Facebook:    {protocol}://{domain}/accounts/facebook/login/callback/")
                print(f"  - Twitter/X:   {protocol}://{domain}/accounts/twitter/login/callback/")
                print(f"  - LinkedIn:    {protocol}://{domain}/accounts/linkedin_oauth2/login/callback/")
                print(f"{'='*70}\n")
        except Exception as e:
            # Site table might not exist yet during first migration
            pass

