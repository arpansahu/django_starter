#!/usr/bin/env python
"""
Setup Twitter and LinkedIn OAuth using database SocialApp entries
for faster testing without application restart.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_starter.settings')
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config

def main():
    # Get current site
    site = Site.objects.get_current()
    print(f'Setting up OAuth for site: {site.domain}')
    print('=' * 75)
    
    # Delete existing Twitter and LinkedIn apps to avoid conflicts
    deleted_count = SocialApp.objects.filter(provider__in=['twitter', 'openid_connect']).delete()[0]
    print(f'✓ Cleared {deleted_count} existing Twitter/LinkedIn configurations')
    print()
    
    # Create Twitter SocialApp
    twitter_app = SocialApp.objects.create(
        provider='twitter',
        name='Twitter',
        client_id=config('TWITTER_API_KEY', default=''),
        secret=config('TWITTER_API_SECRET', default=''),
        key=config('TWITTER_API_KEY', default=''),  # Twitter needs key field
    )
    twitter_app.sites.add(site)
    print(f'✓ Created Twitter SocialApp (ID: {twitter_app.id})')
    print(f'  Client ID: {twitter_app.client_id[:20]}...')
    print(f'  Key: {twitter_app.key[:20]}...')
    print()
    
    # Create LinkedIn OpenID Connect SocialApp
    linkedin_app = SocialApp.objects.create(
        provider='openid_connect',
        provider_id='linkedin',  # This identifies it as LinkedIn
        name='LinkedIn (OpenID Connect)',
        client_id=config('LINKEDIN_CLIENT_ID', default=''),
        secret=config('LINKEDIN_CLIENT_SECRET', default=''),
        settings={
            'server_url': 'https://www.linkedin.com/oauth',
            'authorization_endpoint': 'https://www.linkedin.com/oauth/v2/authorization',
            'token_endpoint': 'https://www.linkedin.com/oauth/v2/accessToken',
            'userinfo_endpoint': 'https://api.linkedin.com/v2/userinfo',
        }
    )
    linkedin_app.sites.add(site)
    print(f'✓ Created LinkedIn OpenID Connect SocialApp (ID: {linkedin_app.id})')
    print(f'  Provider ID: {linkedin_app.provider_id}')
    print(f'  Client ID: {linkedin_app.client_id[:20]}...')
    print(f'  Endpoints configured:')
    for key in linkedin_app.settings.keys():
        print(f'    - {key}')
    print()
    
    print('=' * 75)
    print('✓ Database configuration complete!')
    print()
    print('Benefits of DB configuration:')
    print('  • Modify configs in admin panel without code changes')
    print('  • Changes take effect immediately (no restart needed)')
    print('  • Test different settings quickly')
    print()
    print(f'Admin panel: https://{site.domain}/admin/socialaccount/socialapp/')
    print('=' * 75)

if __name__ == '__main__':
    main()
