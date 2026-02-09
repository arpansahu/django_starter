# check_service_health/management/commands/test_harbor.py

from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from urllib.parse import urljoin


class Command(BaseCommand):
    help = 'Test if Harbor Docker Registry is working properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed output'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Connection timeout in seconds (default: 10)'
        )

    def handle(self, *args, **options):
        verbose = options.get('detailed', False)
        timeout = options.get('timeout', 10)
        
        self.stdout.write(self.style.WARNING('Testing Harbor connection...'))
        
        # Get Harbor settings from environment
        harbor_url = getattr(settings, 'HARBOR_URL', None)
        harbor_username = getattr(settings, 'HARBOR_USERNAME', None)
        harbor_password = getattr(settings, 'HARBOR_PASSWORD', None)
        
        if not harbor_url:
            self.stdout.write(self.style.ERROR(
                '❌ HARBOR_URL not configured in settings'
            ))
            return
        
        if not harbor_username or not harbor_password:
            self.stdout.write(self.style.ERROR(
                '❌ HARBOR_USERNAME or HARBOR_PASSWORD not configured'
            ))
            return
        
        # Ensure URL has proper format
        if not harbor_url.startswith(('http://', 'https://')):
            harbor_url = f'https://{harbor_url}'
        
        try:
            # 1. Test basic connectivity (health endpoint)
            self.stdout.write('Checking Harbor health...')
            health_url = urljoin(harbor_url, '/api/v2.0/health')
            
            response = requests.get(
                health_url,
                timeout=timeout,
                verify=True
            )
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                self.stdout.write(self.style.SUCCESS(f'  ✅ Harbor health: {status}'))
                
                if verbose and 'components' in health_data:
                    for component in health_data['components']:
                        comp_name = component.get('name', 'unknown')
                        comp_status = component.get('status', 'unknown')
                        status_style = self.style.SUCCESS if comp_status == 'healthy' else self.style.ERROR
                        self.stdout.write(f'     - {comp_name}: {status_style(comp_status)}')
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  Health endpoint returned: {response.status_code}'
                ))
            
            # 2. Test authentication
            self.stdout.write('Testing authentication...')
            auth = (harbor_username, harbor_password)
            
            # Get current user info
            user_url = urljoin(harbor_url, '/api/v2.0/users/current')
            response = requests.get(
                user_url,
                auth=auth,
                timeout=timeout,
                verify=True
            )
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username', 'unknown')
                admin = user_data.get('admin_role_in_auth', False)
                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ Authenticated as: {username} (admin: {admin})'
                ))
            elif response.status_code == 401:
                self.stdout.write(self.style.ERROR(
                    '  ❌ Authentication failed - invalid credentials'
                ))
                return
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  Auth endpoint returned: {response.status_code}'
                ))
            
            # 3. List projects
            self.stdout.write('Listing projects...')
            projects_url = urljoin(harbor_url, '/api/v2.0/projects')
            response = requests.get(
                projects_url,
                auth=auth,
                timeout=timeout,
                verify=True
            )
            
            if response.status_code == 200:
                projects = response.json()
                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ Found {len(projects)} project(s)'
                ))
                
                if verbose and projects:
                    for project in projects[:5]:
                        proj_name = project.get('name', 'unknown')
                        repo_count = project.get('repo_count', 0)
                        self.stdout.write(f'     - {proj_name} ({repo_count} repositories)')
                    if len(projects) > 5:
                        self.stdout.write(f'     ... and {len(projects) - 5} more')
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  Projects endpoint returned: {response.status_code}'
                ))
            
            # 4. Check system info
            self.stdout.write('Checking system info...')
            sysinfo_url = urljoin(harbor_url, '/api/v2.0/systeminfo')
            response = requests.get(
                sysinfo_url,
                auth=auth,
                timeout=timeout,
                verify=True
            )
            
            if response.status_code == 200:
                sysinfo = response.json()
                version = sysinfo.get('harbor_version', 'unknown')
                registry_url = sysinfo.get('registry_url', 'unknown')
                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ Harbor version: {version}'
                ))
                
                if verbose:
                    self.stdout.write(f'     Registry URL: {registry_url}')
                    self.stdout.write(f'     Auth mode: {sysinfo.get("auth_mode", "unknown")}')
                    self.stdout.write(f'     Has CA root: {sysinfo.get("has_ca_root", False)}')
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  System info returned: {response.status_code}'
                ))
            
            # 5. Check registry connectivity (ping)
            self.stdout.write('Checking registry connectivity...')
            ping_url = urljoin(harbor_url, '/v2/')
            response = requests.get(
                ping_url,
                auth=auth,
                timeout=timeout,
                verify=True
            )
            
            if response.status_code in [200, 401]:  # 401 is expected without token
                self.stdout.write(self.style.SUCCESS(
                    '  ✅ Registry API responding'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  Registry ping returned: {response.status_code}'
                ))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Harbor is healthy!'))
            
        except requests.exceptions.SSLError as e:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Harbor SSL error: {e}'
            ))
            self.stdout.write(self.style.WARNING(
                '\nCheck if your certificate is valid or try with --insecure'
            ))
        except requests.exceptions.ConnectionError as e:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Harbor connection failed: Could not connect to {harbor_url}'
            ))
            self.stdout.write(self.style.WARNING(
                '\nMake sure Harbor is running and accessible'
            ))
        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Harbor connection timed out after {timeout}s'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Harbor test failed: {e}'))
