#!/bin/bash
# Script to debug and fix Django Starter production issues
# ⚠️  MUST BE RUN ON SERVER WITH KUBECTL ACCESS (Jenkins/K8s node)
# Usage: ./debug_production.sh [command]
# Commands: logs, migrations, showmigrations, check-env, check-users, fix-oauth, restart

set -e

echo "========================================"
echo "Django Starter Production Debug Script"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get pod name
echo "🔍 Finding Django Starter pod..."
POD_NAME=$(kubectl get pods -l app=django-starter -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo -e "${RED}❌ No pod found with label app=django-starter${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found pod: $POD_NAME${NC}"
echo

# Function to run command in pod
run_in_pod() {
    kubectl exec -it $POD_NAME -- bash -c "$1"
}

# Check what user is asking to do
case "${1:-help}" in
    logs)
        echo "📋 Fetching last 100 lines of pod logs..."
        echo "========================================"
        kubectl logs $POD_NAME --tail=100
        ;;
        
    logs-full)
        echo "📋 Fetching all pod logs..."
        echo "========================================"
        kubectl logs $POD_NAME
        ;;
        
    migrations)
        echo "🔄 Running Django migrations..."
        echo "========================================"
        run_in_pod "cd /app && python manage.py migrate"
        echo -e "${GREEN}✅ Migrations completed${NC}"
        ;;
        
    showmigrations)
        echo "📋 Showing migration status..."
        echo "========================================"
        run_in_pod "cd /app && python manage.py showmigrations"
        ;;
        
    check-env)
        echo "🔍 Checking environment variables..."
        echo "========================================"
        run_in_pod "cd /app && python -c \"
from django.conf import settings
import os
print(f'DEBUG: {settings.DEBUG}')
print(f'DOMAIN: {settings.DOMAIN}')
print(f'PROTOCOL: {settings.PROTOCOL}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'SECURE_PROXY_SSL_HEADER: {getattr(settings, \"SECURE_PROXY_SSL_HEADER\", \"Not set\")}')
print(f'SESSION_COOKIE_SECURE: {getattr(settings, \"SESSION_COOKIE_SECURE\", \"Not set\")}')
print(f'CSRF_COOKIE_SECURE: {getattr(settings, \"CSRF_COOKIE_SECURE\", \"Not set\")}')
\""
        ;;
        
    check-users)
        echo "👥 Checking user accounts..."
        echo "========================================"
        run_in_pod "cd /app && python manage.py shell -c \"
from account.models import Account
print(f'Total users: {Account.objects.count()}')
print(f'Active users: {Account.objects.filter(is_active=True).count()}')
print(f'Inactive users: {Account.objects.filter(is_active=False).count()}')
print('\\nRecent users:')
for user in Account.objects.order_by('-date_joined')[:5]:
    print(f'  - {user.email} (username: {user.username}, active: {user.is_active})')
\""
        ;;
        
    shell)
        echo "💻 Opening Django shell..."
        echo "========================================"
        kubectl exec -it $POD_NAME -- python manage.py shell
        ;;
        
    bash)
        echo "💻 Opening bash shell in pod..."
        echo "========================================"
        kubectl exec -it $POD_NAME -- bash
        ;;
        
    restart)
        echo "🔄 Restarting deployment..."
        echo "========================================"
        kubectl rollout restart deployment django-starter-app
        echo "Waiting for rollout to complete..."
        kubectl rollout status deployment django-starter-app
        echo -e "${GREEN}✅ Deployment restarted${NC}"
        ;;
        
    pod-info)
        echo "📊 Pod Information..."
        echo "========================================"
        kubectl describe pod $POD_NAME
        ;;
        
    fix-oauth)
        echo "🔧 Applying OAuth fixes..."
        echo "========================================"
        
        echo "Step 1: Running migrations..."
        run_in_pod "cd /app && python manage.py migrate"
        
        echo
        echo "Step 2: Updating Site domain..."
        run_in_pod "cd /app && python manage.py shell -c \"
from django.contrib.sites.models import Site
from django.conf import settings
site = Site.objects.get(id=1)
if site.domain != settings.DOMAIN:
    old_domain = site.domain
    site.domain = settings.DOMAIN
    site.name = f'Django Starter ({settings.DOMAIN})'
    site.save()
    print(f'✅ Updated Site domain from {old_domain} to {settings.DOMAIN}')
else:
    print(f'✅ Site domain already set to {settings.DOMAIN}')
\""
        
        echo
        echo "Step 3: Checking OAuth settings..."
        run_in_pod "cd /app && python show_oauth_urls.py"
        
        echo
        echo -e "${GREEN}✅ OAuth fixes applied!${NC}"
        echo -e "${YELLOW}⚠️  Make sure to add these OAuth callback URLs to your provider consoles!${NC}"
        ;;
        
    help|*)
        echo "Available commands:"
        echo
        echo "  logs              - Show last 100 lines of pod logs"
        echo "  logs-full         - Show all pod logs"
        echo "  migrations        - Run Django migrations"
        echo "  showmigrations    - Show migration status"
        echo "  check-env         - Check environment variables and settings"
        echo "  check-users       - Check user accounts status"
        echo "  shell             - Open Django shell"
        echo "  bash              - Open bash shell in pod"
        echo "  restart           - Restart the deployment"
        echo "  pod-info          - Show detailed pod information"
        echo "  fix-oauth         - Apply all OAuth and migration fixes"
        echo
        echo "Usage: ./debug_production.sh [command]"
        echo
        echo "Quick fix for OAuth issues:"
        echo "  ./debug_production.sh fix-oauth"
        ;;
esac
