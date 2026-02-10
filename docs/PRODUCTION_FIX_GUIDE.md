# Production Issues - Diagnosis and Fix Guide

## Problem Summary

- **Forms not working in production** (but work locally)
- **Google OAuth still showing Error 500**
- **Migration for `is_active` field not applied**

## Root Cause

The Kubernetes pod is running the **OLD image** which doesn't include:
1. Migration `0002_alter_account_is_active.py` (is_active default changed to True)
2. Updated Account.create_user() method (password optional for OAuth)
3. Updated SocialAccountAdapter with username generation
4. HTTPS security settings

## Step-by-Step Fix

### Option 1: Quick Fix (Run on your server with kubectl access)

```bash
# SSH to your Jenkins/K8s server
ssh your-server

# Navigate to project directory
cd /path/to/django_starter

# Pull latest changes
git pull

# Get pod name
POD_NAME=$(kubectl get pods -l app=django-starter -o jsonpath='{.items[0].metadata.name}')
echo "Pod: $POD_NAME"

# Step 1: Run migrations
kubectl exec -it $POD_NAME -- python manage.py migrate

# Step 2: Update Site domain
kubectl exec -it $POD_NAME -- python manage.py shell -c "
from django.contrib.sites.models import Site
from django.conf import settings
site = Site.objects.get(id=1)
site.domain = settings.DOMAIN
site.name = f'Django Starter ({settings.DOMAIN})'
site.save()
print(f'Site updated: {site.domain}')
"

# Step 3: Restart pod to apply all code changes
kubectl rollout restart deployment django-starter-app

# Step 4: Wait for rollout to complete
kubectl rollout status deployment django-starter-app

# Step 5: Check pod logs
kubectl logs -f deployment/django-starter-app
```

### Option 2: Re-trigger Jenkins Build (Recommended - ensures new image)

```bash
# SSH to your Jenkins/K8s server
ssh your-server

# Navigate to project
cd /path/to/django_starter

# Pull latest changes
git pull

# Manually trigger Jenkins build
# Or trigger via Jenkins UI:
# 1. Go to https://jenkins.arpansahu.space/job/django_starter_build/
# 2. Click "Build with Parameters"
# 3. Leave RUN_TESTS=false (for speed)
# 4. Click "Build"
```

This will:
1. Build new Docker image with all fixes
2. Push to Harbor registry
3. Auto-deploy via django_starter_deploy pipeline
4. Run migrations

## Manual Migration Commands (if needed)

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=django-starter -o jsonpath='{.items[0].metadata.name}')

# Check migration status
kubectl exec -it $POD_NAME -- python manage.py showmigrations

# Run specific migration
kubectl exec -it $POD_NAME -- python manage.py migrate account 0002

# Check if is_active field updated
kubectl exec -it $POD_NAME -- python manage.py shell -c "
from account.models import Account
print(f'Field default: {Account._meta.get_field(\"is_active\").default}')
"
```

## Check Current Production Status

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=django-starter -o jsonpath='{.items[0].metadata.name}')

# Check Django settings
kubectl exec -it $POD_NAME -- python -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'DOMAIN: {settings.DOMAIN}')
print(f'PROTOCOL: {settings.PROTOCOL}')
print(f'SECURE_PROXY_SSL_HEADER: {getattr(settings, \"SECURE_PROXY_SSL_HEADER\", None)}')
"

# Check Site domain
kubectl exec -it $POD_NAME -- python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
print(f'Site domain: {site.domain}')
"

# Check user accounts
kubectl exec -it $POD_NAME -- python manage.py shell -c "
from account.models import Account
print(f'Total users: {Account.objects.count()}')
print(f'Active: {Account.objects.filter(is_active=True).count()}')
print(f'Inactive: {Account.objects.filter(is_active=False).count()}')
"

# Check pod logs for errors
kubectl logs $POD_NAME --tail=100
```

## Verify OAuth Is Working

After applying fixes:

```bash
# 1. Check OAuth URLs are correct
kubectl exec -it $POD_NAME -- python show_oauth_urls.py

# 2. Try OAuth login at:
https://django-starter.arpansahu.space/account/login/

# 3. Check logs during OAuth attempt:
kubectl logs -f $POD_NAME
```

## Common Issues and Solutions

### Issue 1: Migration not applied
**Symptom:** Google login shows Error 500, users have is_active=False
**Fix:**
```bash
kubectl exec -it $POD_NAME -- python manage.py migrate account 0002
kubectl rollout restart deployment django-starter-app
```

### Issue 2: Site domain not updated
**Symptom:** Facebook says "not using secure connection"
**Fix:**
```bash
kubectl exec -it $POD_NAME -- python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'django-starter.arpansahu.space'
site.save()
"
```

### Issue 3: Old code still cached
**Symptom:** Changes not reflected after deployment
**Fix:**
```bash
# Force pull new image and restart
kubectl rollout restart deployment django-starter-app
kubectl rollout status deployment django-starter-app

# Or delete pod (will recreate with new image)
kubectl delete pod $POD_NAME
```

### Issue 4: DEBUG=True in production
**Symptom:** HTTPS security not working
**Fix:**
```bash
# Check .env in Jenkins credentials
# Update jenkins credential 'django_starter_env_file'
# Set DEBUG=False
# Re-trigger build
```

## Verification Checklist

After applying fixes, verify:

- [ ] `kubectl exec -it $POD_NAME -- python manage.py showmigrations` shows account.0002 applied
- [ ] `kubectl exec -it $POD_NAME -- python show_oauth_urls.py` shows correct HTTPS URLs
- [ ] Site domain is set to `django-starter.arpansahu.space`
- [ ] DEBUG=False in production
- [ ] SECURE_PROXY_SSL_HEADER is set
- [ ] Google OAuth login works without Error 500
- [ ] Forms work correctly
- [ ] Pod logs show no errors: `kubectl logs $POD_NAME`

## Quick Debug Script

Use the provided `debug_production.sh` script (run on server with kubectl):

```bash
# Show migration status
./debug_production.sh showmigrations

# Run migrations
./debug_production.sh migrations

# Check environment
./debug_production.sh check-env

# Check users
./debug_production.sh check-users

# View logs
./debug_production.sh logs

# Apply all fixes
./debug_production.sh fix-oauth

# Restart deployment
./debug_production.sh restart
```

## Expected Outcome

After following these steps:
- ✅ Google OAuth login should work
- ✅ Facebook OAuth should work (no SSL error)
- ✅ New users via OAuth are automatically active
- ✅ Forms work correctly
- ✅ HTTPS security headers present
- ✅ No Error 500 on OAuth callback

## Support

If issues persist:
1. Check pod logs: `kubectl logs -f $POD_NAME`
2. Check Django logs in pod: `/app/logs/`
3. Verify OAuth callback URLs match in provider consoles
4. Ensure `.env` file has correct values in Jenkins credentials
