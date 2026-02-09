# check_service_health/management/commands/test_elasticsearch.py

from django.core.management.base import BaseCommand
from django.conf import settings
import json


class Command(BaseCommand):
    help = 'Test if Elasticsearch is working properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed output'
        )

    def handle(self, *args, **options):
        verbose = options.get('detailed', False)
        
        self.stdout.write(self.style.WARNING('Testing Elasticsearch connection...'))
        
        try:
            from elasticsearch import Elasticsearch
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '❌ elasticsearch package not installed. Run: pip install elasticsearch'
            ))
            return
        
        # Get Elasticsearch settings
        es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'localhost')
        es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
        es_user = getattr(settings, 'ELASTICSEARCH_USER', None)
        es_password = getattr(settings, 'ELASTICSEARCH_PASSWORD', None)
        
        # Build URL - check if host already includes protocol
        if es_host.startswith('http://') or es_host.startswith('https://'):
            es_url = es_host
            # Don't add port if it's already a full URL
        else:
            es_url = f"http://{es_host}:{es_port}"
        
        try:
            # Create client with optional authentication
            client_kwargs = {
                'hosts': [es_url],
                'verify_certs': False,
                'ssl_show_warn': False,
                'request_timeout': 30,
            }
            
            if es_user and es_password:
                client_kwargs['http_auth'] = (es_user, es_password)
            
            # Use urllib3 to disable SSL warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            es = Elasticsearch(**client_kwargs)
            
            # 1. Check cluster health
            self.stdout.write('Checking cluster health...')
            health = es.cluster.health()
            status = health.get('status', 'unknown')
            
            if status == 'green':
                self.stdout.write(self.style.SUCCESS(f'  ✅ Cluster status: {status}'))
            elif status == 'yellow':
                self.stdout.write(self.style.WARNING(f'  ⚠️  Cluster status: {status} (some replicas unavailable)'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ Cluster status: {status}'))
            
            if verbose:
                self.stdout.write(f'     Cluster name: {health.get("cluster_name")}')
                self.stdout.write(f'     Number of nodes: {health.get("number_of_nodes")}')
                self.stdout.write(f'     Active shards: {health.get("active_shards")}')
            
            # 2. Check if we can list indices
            self.stdout.write('Checking indices...')
            indices = es.cat.indices(format='json')
            index_count = len(indices) if indices else 0
            self.stdout.write(self.style.SUCCESS(f'  ✅ Found {index_count} indices'))
            
            if verbose and indices:
                for idx in indices[:5]:  # Show first 5
                    self.stdout.write(f'     - {idx.get("index")} ({idx.get("docs.count", 0)} docs)')
                if len(indices) > 5:
                    self.stdout.write(f'     ... and {len(indices) - 5} more')
            
            # 3. Test write/read/delete (using a test index)
            test_index = 'django_health_check_test'
            test_doc = {'message': 'health_check_test', 'timestamp': '2026-02-08'}
            
            self.stdout.write('Testing write operation...')
            es.index(index=test_index, id='test_doc_1', document=test_doc, refresh=True)
            self.stdout.write(self.style.SUCCESS('  ✅ Write successful'))
            
            self.stdout.write('Testing read operation...')
            result = es.get(index=test_index, id='test_doc_1')
            if result['_source']['message'] == 'health_check_test':
                self.stdout.write(self.style.SUCCESS('  ✅ Read successful'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Read returned unexpected data'))
            
            self.stdout.write('Testing search operation...')
            search_result = es.search(index=test_index, query={'match': {'message': 'health_check_test'}})
            hits = search_result.get('hits', {}).get('total', {}).get('value', 0)
            self.stdout.write(self.style.SUCCESS(f'  ✅ Search successful ({hits} hits)'))
            
            self.stdout.write('Cleaning up test data...')
            es.indices.delete(index=test_index, ignore=[404])
            self.stdout.write(self.style.SUCCESS('  ✅ Cleanup successful'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Elasticsearch is healthy!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Elasticsearch connection failed: {e}'))
            self.stdout.write(self.style.WARNING(f'\nMake sure Elasticsearch is running at {es_url}'))
