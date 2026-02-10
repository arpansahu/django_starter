#!/usr/bin/env python
"""
Display OAuth callback URLs for the current environment.
Run this script to see what URLs to add to your OAuth provider consoles.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_starter.settings')
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site

def main():
    site = Site.objects.get(id=settings.SITE_ID)
    domain = site.domain
    # Clean protocol - remove :// if present, we'll add it back
    protocol = settings.PROTOCOL.replace('://', '').replace('/', '')
    
    print("\n" + "="*80)
    print("OAUTH CALLBACK URLs - Add these to your provider consoles:")
    print("="*80)
    print(f"\nCurrent Environment: {domain}")
    print(f"Protocol: {protocol}://")
    print("\n" + "-"*80)
    
    providers = [
        ("Google", "google", "https://console.developers.google.com/"),
        ("GitHub", "github", "https://github.com/settings/developers"),
        ("Facebook", "facebook", "https://developers.facebook.com/apps/"),
        ("Twitter/X", "twitter", "https://developer.twitter.com/en/portal/dashboard"),
        ("LinkedIn", "linkedin_oauth2", "https://www.linkedin.com/developers/apps"),
    ]
    
    for name, provider_id, console_url in providers:
        callback_url = f"{protocol}://{domain}/accounts/{provider_id}/login/callback/"
        print(f"\n{name}:")
        print(f"  Callback URL: {callback_url}")
        print(f"  Console:      {console_url}")
    
    print("\n" + "="*80)
    print("\nFor local development, also add 127.0.0.1 variant if using localhost:")
    if "localhost" in domain:
        alt_domain = domain.replace("localhost", "127.0.0.1")
        print(f"  Example: {protocol}://{alt_domain}/accounts/google/login/callback/")
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
