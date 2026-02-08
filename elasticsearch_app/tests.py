"""
Elasticsearch App Tests
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import IndexedDocument, SearchQuery, SearchSynonym
from .client import check_elasticsearch_connection, get_cluster_health
from .documents import INDEX_PREFIX


User = get_user_model()


class IndexedDocumentModelTest(TestCase):
    """Test IndexedDocument model"""
    
    def test_create_indexed_document(self):
        """Test creating an indexed document record"""
        doc = IndexedDocument.objects.create(
            doc_type='note',
            source_id='123',
            es_index='django_starter_notes',
            status='indexed'
        )
        self.assertEqual(str(doc), 'note:123 (indexed)')
        self.assertEqual(doc.status, 'indexed')
    
    def test_indexed_document_unique_together(self):
        """Test unique constraint on doc_type and source_id"""
        IndexedDocument.objects.create(
            doc_type='note',
            source_id='456',
            es_index='django_starter_notes',
            status='indexed'
        )
        # Should raise error for duplicate
        with self.assertRaises(Exception):
            IndexedDocument.objects.create(
                doc_type='note',
                source_id='456',
                es_index='django_starter_notes',
                status='pending'
            )


class SearchQueryModelTest(TestCase):
    """Test SearchQuery model"""
    
    def test_create_search_query(self):
        """Test creating a search query log"""
        query = SearchQuery.objects.create(
            query='test search',
            index='all',
            results_count=10,
            response_time_ms=50
        )
        self.assertIn('test search', str(query))
        self.assertEqual(query.results_count, 10)
    
    def test_search_query_with_user(self):
        """Test search query with associated user"""
        user = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='testpass123'
        )
        query = SearchQuery.objects.create(
            query='user search',
            user=user,
            results_count=5
        )
        self.assertEqual(query.user, user)


class SearchSynonymModelTest(TestCase):
    """Test SearchSynonym model"""
    
    def test_create_synonym(self):
        """Test creating a search synonym"""
        synonym = SearchSynonym.objects.create(
            term='laptop',
            synonyms='notebook, computer, macbook'
        )
        self.assertIn('laptop', str(synonym))
    
    def test_get_synonyms_list(self):
        """Test getting synonyms as list"""
        synonym = SearchSynonym.objects.create(
            term='car',
            synonyms='automobile, vehicle, auto'
        )
        synonyms_list = synonym.get_synonyms_list()
        self.assertEqual(len(synonyms_list), 3)
        self.assertIn('automobile', synonyms_list)


class ElasticsearchClientTest(TestCase):
    """Test Elasticsearch client functions"""
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_check_connection_success(self, mock_es):
        """Test successful connection check"""
        mock_client = MagicMock()
        mock_client.info.return_value = {
            'cluster_name': 'test-cluster',
            'version': {'number': '7.17.0'},
            'tagline': 'You Know, for Search'
        }
        mock_es.return_value = mock_client
        
        # Reset the client cache
        from elasticsearch_app.client import reset_elasticsearch_client
        reset_elasticsearch_client()
        
        result = check_elasticsearch_connection()
        self.assertTrue(result['connected'])
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_check_connection_failure(self, mock_es):
        """Test failed connection check"""
        mock_es.side_effect = Exception('Connection refused')
        
        from elasticsearch_app.client import reset_elasticsearch_client
        reset_elasticsearch_client()
        
        result = check_elasticsearch_connection()
        self.assertFalse(result['connected'])
        self.assertIn('error', result)


class ElasticsearchViewsTest(TestCase):
    """Test Elasticsearch views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_search_view_get(self):
        """Test search view GET request"""
        response = self.client.get(reverse('elasticsearch_app:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elasticsearch_app/search.html')
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('elasticsearch_app:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard with authenticated user"""
        self.client.login(email='test@example.com', password='testpass123')
        
        with patch('elasticsearch_app.views.check_elasticsearch_connection') as mock_check:
            mock_check.return_value = {'connected': False, 'error': 'Test'}
            response = self.client.get(reverse('elasticsearch_app:dashboard'))
            self.assertEqual(response.status_code, 200)
    
    def test_analytics_requires_login(self):
        """Test analytics view requires authentication"""
        response = self.client.get(reverse('elasticsearch_app:analytics'))
        self.assertEqual(response.status_code, 302)


class ElasticsearchAPITest(TestCase):
    """Test Elasticsearch API endpoints"""
    
    def test_search_api_requires_query(self):
        """Test search API requires query parameter"""
        response = self.client.get(reverse('elasticsearch_app:api_search'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
    
    def test_suggest_api_short_query(self):
        """Test suggest API with short query"""
        response = self.client.get(
            reverse('elasticsearch_app:api_suggest'),
            {'q': 'a'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['suggestions'], [])
    
    def test_health_api(self):
        """Test cluster health API"""
        with patch('elasticsearch_app.views.get_cluster_health') as mock_health:
            mock_health.return_value = {'status': 'green'}
            response = self.client.get(reverse('elasticsearch_app:api_health'))
            self.assertEqual(response.status_code, 200)


class ElasticsearchDocumentsTest(TestCase):
    """Test Elasticsearch document definitions"""
    
    def test_index_prefix(self):
        """Test index prefix is set correctly"""
        self.assertEqual(INDEX_PREFIX, 'django_starter')
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_create_all_indices(self, mock_es_class):
        """Test create_all_indices function"""
        from .documents import create_all_indices
        from .client import reset_elasticsearch_client
        
        # Reset the client cache
        reset_elasticsearch_client()
        
        mock_es = MagicMock()
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_es_class.return_value = mock_es
        
        result = create_all_indices()
        self.assertTrue(result)


class ElasticsearchTasksTest(TestCase):
    """Test Elasticsearch Celery tasks"""
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_index_document_task(self, mock_es_class):
        """Test index_document task"""
        from .tasks import index_document
        from .client import reset_elasticsearch_client
        
        # Reset the client cache
        reset_elasticsearch_client()
        
        mock_es = MagicMock()
        mock_es.index.return_value = {'_id': 'test-id-123'}
        mock_es_class.return_value = mock_es
        
        result = index_document('note', '1', {'title': 'Test Note'})
        self.assertTrue(result['success'])
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_delete_document_task(self, mock_es_class):
        """Test delete_document task"""
        from .tasks import delete_document
        from .client import reset_elasticsearch_client
        
        # Reset the client cache
        reset_elasticsearch_client()
        
        mock_es = MagicMock()
        mock_es_class.return_value = mock_es
        
        # Create a document to delete
        IndexedDocument.objects.create(
            doc_type='note',
            source_id='1',
            es_index='django_starter_notes',
            status='indexed'
        )
        
        result = delete_document('note', '1')
        self.assertTrue(result['success'])



# ======================================================================
# AUTO-GENERATED TESTS - Django Test Enforcer (IMPLEMENTED)
# Generated on: 2026-02-08 18:31:28
# These tests have been implemented.
# ======================================================================


from django.urls import reverse

class TestElasticsearchAppClassBasedViews(TestCase):
    """Tests for elasticsearch_app class-based views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)

    def test_cluster_health_apiview(self):
        """Test ClusterHealthAPIView - API endpoint for cluster health"""
        with patch('elasticsearch_app.views.get_cluster_health') as mock_health:
            mock_health.return_value = {'status': 'green', 'cluster_name': 'test'}
            response = self.client.get(reverse('elasticsearch_app:api_health'))
            self.assertEqual(response.status_code, 200)

    def test_elasticsearch_dashboard_view(self):
        """Test ElasticsearchDashboardView - Dashboard page"""
        with patch('elasticsearch_app.views.check_elasticsearch_connection') as mock_check:
            mock_check.return_value = {'connected': False, 'error': 'Test'}
            response = self.client.get(reverse('elasticsearch_app:dashboard'))
            self.assertEqual(response.status_code, 200)

    def test_index_management_view_create(self):
        """Test IndexManagementView - Create indices action"""
        with patch('elasticsearch_app.views.create_all_indices') as mock_create:
            mock_create.return_value = True
            response = self.client.post(
                reverse('elasticsearch_app:manage'),
                {'action': 'create_indices'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)

    def test_indices_apiview(self):
        """Test IndicesAPIView - API endpoint for indices listing"""
        with patch('elasticsearch_app.views.get_index_stats') as mock_stats:
            mock_stats.return_value = [{'index': 'test', 'health': 'green'}]
            response = self.client.get(reverse('elasticsearch_app:api_indices'))
            self.assertEqual(response.status_code, 200)

    def test_search_analytics_view(self):
        """Test SearchAnalyticsView - Analytics page"""
        SearchQuery.objects.create(query='test', results_count=10, response_time_ms=50)
        response = self.client.get(reverse('elasticsearch_app:analytics'))
        self.assertEqual(response.status_code, 200)


class TestElasticsearchAppFunctions(TestCase):
    """Tests for elasticsearch_app functions"""

    def setUp(self):
        reset_elasticsearch_client()

    @patch('elasticsearch_app.client.Elasticsearch')
    def test_delete_all_indices(self, mock_es_class):
        """Test delete_all_indices function"""
        mock_es = MagicMock()
        mock_es.indices.delete.return_value = {'acknowledged': True}
        mock_es_class.return_value = mock_es
        
        from elasticsearch_app.documents import delete_all_indices
        result = delete_all_indices()
        self.assertTrue(result)

    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_cluster_health(self, mock_es_class):
        """Test get_cluster_health function"""
        mock_es = MagicMock()
        mock_es.cluster.health.return_value = {'status': 'green', 'cluster_name': 'test'}
        mock_es_class.return_value = mock_es
        
        from elasticsearch_app.client import get_cluster_health
        result = get_cluster_health()
        self.assertIn('status', result)

    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_elasticsearch_client(self, mock_es_class):
        """Test get_elasticsearch_client function"""
        mock_es = MagicMock()
        mock_es_class.return_value = mock_es
        
        from elasticsearch_app.client import get_elasticsearch_client
        client = get_elasticsearch_client()
        self.assertIsNotNone(client)

    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_index_stats(self, mock_es_class):
        """Test get_index_stats function"""
        mock_es = MagicMock()
        mock_es.cat.indices.return_value = [{'index': 'test', 'health': 'green'}]
        mock_es_class.return_value = mock_es
        
        from elasticsearch_app.client import get_index_stats
        result = get_index_stats()
        self.assertIsInstance(result, list)


# ======================================================================
# EXTENDED TESTS - Merged from tests_extended.py
# Comprehensive tests to improve coverage for search service, views, and tasks.
# ======================================================================

import json
from .client import (
    get_elasticsearch_client, check_elasticsearch_connection,
    get_cluster_health, get_index_stats, reset_elasticsearch_client
)
from .documents import (
    INDEX_PREFIX, SearchableDocument, NoteDocument, UserDocument, LogDocument,
    create_all_indices, delete_all_indices
)
from .search import SearchService


class SearchServiceTests(TestCase):
    """Comprehensive tests for SearchService"""
    
    def setUp(self):
        reset_elasticsearch_client()
    
    @patch('elasticsearch_app.search.get_elasticsearch_client')
    def test_search_all_with_query(self, mock_get_client):
        """Test search_all with a query string"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.hits.total.value = 1
        mock_response.__iter__ = MagicMock(return_value=iter([]))
        
        mock_get_client.return_value = mock_client
        
        with patch('elasticsearch_app.search.Search') as mock_search_class:
            mock_search = MagicMock()
            mock_search.query.return_value = mock_search
            mock_search.filter.return_value = mock_search
            mock_search.highlight.return_value = mock_search
            mock_search.__getitem__ = MagicMock(return_value=mock_search)
            mock_search.execute.return_value = mock_response
            mock_search_class.return_value = mock_search
            
            service = SearchService()
            results = service.search_all('test query')
            
            self.assertIn('hits', results)
            self.assertIn('total', results)
            self.assertIn('page', results)
    
    @patch('elasticsearch_app.search.get_elasticsearch_client')
    def test_search_notes(self, mock_get_client):
        """Test search_notes method"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.hits.total.value = 5
        mock_response.__iter__ = MagicMock(return_value=iter([]))
        
        mock_get_client.return_value = mock_client
        
        with patch('elasticsearch_app.search.Search') as mock_search_class:
            mock_search = MagicMock()
            mock_search.query.return_value = mock_search
            mock_search.filter.return_value = mock_search
            mock_search.highlight.return_value = mock_search
            mock_search.__getitem__ = MagicMock(return_value=mock_search)
            mock_search.execute.return_value = mock_response
            mock_search_class.return_value = mock_search
            
            service = SearchService()
            results = service.search_notes('test note', page=1, per_page=10)
            
            self.assertEqual(results['total'], 5)
    
    @patch('elasticsearch_app.search.get_elasticsearch_client')
    def test_search_users(self, mock_get_client):
        """Test search_users method"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.hits.total.value = 3
        mock_response.__iter__ = MagicMock(return_value=iter([]))
        
        mock_get_client.return_value = mock_client
        
        with patch('elasticsearch_app.search.Search') as mock_search_class:
            mock_search = MagicMock()
            mock_search.query.return_value = mock_search
            mock_search.highlight.return_value = mock_search
            mock_search.__getitem__ = MagicMock(return_value=mock_search)
            mock_search.execute.return_value = mock_response
            mock_search_class.return_value = mock_search
            
            service = SearchService()
            results = service.search_users('john', page=1, per_page=10)
            
            self.assertEqual(results['total'], 3)
    
    @patch('elasticsearch_app.search.get_elasticsearch_client')
    def test_search_logs(self, mock_get_client):
        """Test search_logs method"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.hits.total.value = 10
        mock_response.__iter__ = MagicMock(return_value=iter([]))
        
        mock_get_client.return_value = mock_client
        
        with patch('elasticsearch_app.search.Search') as mock_search_class:
            mock_search = MagicMock()
            mock_search.query.return_value = mock_search
            mock_search.filter.return_value = mock_search
            mock_search.sort.return_value = mock_search
            mock_search.__getitem__ = MagicMock(return_value=mock_search)
            mock_search.execute.return_value = mock_response
            mock_search_class.return_value = mock_search
            
            service = SearchService()
            results = service.search_logs('error', page=1, per_page=20)
            
            self.assertEqual(results['total'], 10)


class ElasticsearchClientExtendedTests(TestCase):
    """Extended tests for Elasticsearch client"""
    
    def setUp(self):
        reset_elasticsearch_client()
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_cluster_health_success(self, mock_es_class):
        """Test get_cluster_health success"""
        mock_es = MagicMock()
        mock_es.cluster.health.return_value = {
            'status': 'green',
            'cluster_name': 'test-cluster',
            'number_of_nodes': 3
        }
        mock_es_class.return_value = mock_es
        
        result = get_cluster_health()
        
        self.assertEqual(result['status'], 'green')
        self.assertEqual(result['number_of_nodes'], 3)
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_cluster_health_failure(self, mock_es_class):
        """Test get_cluster_health failure"""
        mock_es = MagicMock()
        mock_es.cluster.health.side_effect = Exception('Connection error')
        mock_es_class.return_value = mock_es
        
        result = get_cluster_health()
        
        self.assertEqual(result['status'], 'unavailable')
        self.assertIn('error', result)
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_index_stats_success(self, mock_es_class):
        """Test get_index_stats success"""
        mock_es = MagicMock()
        mock_es.cat.indices.return_value = [
            {'index': 'django_starter_notes', 'health': 'green', 'docs.count': '100'}
        ]
        mock_es_class.return_value = mock_es
        
        result = get_index_stats()
        
        self.assertEqual(len(result), 1)
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_get_index_stats_failure(self, mock_es_class):
        """Test get_index_stats failure"""
        mock_es = MagicMock()
        mock_es.cat.indices.side_effect = Exception('Error')
        mock_es_class.return_value = mock_es
        
        result = get_index_stats()
        
        self.assertEqual(result, [])


class ElasticsearchViewsExtendedTests(TestCase):
    """Extended tests for Elasticsearch views"""
    
    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='viewtestuser',
            email='viewtest@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_search_view_with_query(self):
        """Test search view with query parameter"""
        with patch('elasticsearch_app.views.SearchService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.search_all.return_value = {
                'hits': [], 'total': 0, 'page': 1, 'per_page': 10, 'pages': 1
            }
            mock_service_class.return_value = mock_service
            
            response = self.client_http.get(
                reverse('elasticsearch_app:search'),
                {'q': 'test query'}
            )
            
            self.assertEqual(response.status_code, 200)
    
    def test_analytics_view_authenticated(self):
        """Test analytics view with authenticated user"""
        self.client_http.login(email='viewtest@example.com', password='testpass123')
        
        SearchQuery.objects.create(query='test1', results_count=10, response_time_ms=50)
        SearchQuery.objects.create(query='test2', results_count=0, response_time_ms=30)
        
        response = self.client_http.get(reverse('elasticsearch_app:analytics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('top_queries', response.context)


class ElasticsearchDocumentsExtendedTests(TestCase):
    """Extended tests for Elasticsearch documents"""
    
    def setUp(self):
        reset_elasticsearch_client()
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_delete_all_indices(self, mock_es_class):
        """Test delete_all_indices function"""
        mock_es = MagicMock()
        mock_es.indices.delete.return_value = {'acknowledged': True}
        mock_es_class.return_value = mock_es
        
        result = delete_all_indices()
        
        self.assertTrue(result)
    
    def test_document_index_names(self):
        """Test document index names are correct"""
        self.assertEqual(SearchableDocument.Index.name, f'{INDEX_PREFIX}_documents')
        self.assertEqual(NoteDocument.Index.name, f'{INDEX_PREFIX}_notes')
        self.assertEqual(UserDocument.Index.name, f'{INDEX_PREFIX}_users')
        self.assertEqual(LogDocument.Index.name, f'{INDEX_PREFIX}_logs')


class ElasticsearchTasksExtendedTests(TestCase):
    """Extended tests for Elasticsearch tasks"""
    
    def setUp(self):
        reset_elasticsearch_client()
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_index_document_creates_record(self, mock_es_class):
        """Test index_document creates IndexedDocument record"""
        from .tasks import index_document
        
        mock_es = MagicMock()
        mock_es.index.return_value = {'_id': 'es-123'}
        mock_es_class.return_value = mock_es
        
        result = index_document('note', '999', {'title': 'Test', 'content': 'Content'})
        
        self.assertTrue(result['success'])
        self.assertTrue(IndexedDocument.objects.filter(doc_type='note', source_id='999').exists())
    
    @patch('elasticsearch_app.client.Elasticsearch')
    def test_index_document_error(self, mock_es_class):
        """Test index_document error handling"""
        from .tasks import index_document
        
        mock_es = MagicMock()
        mock_es.index.side_effect = Exception('Index error')
        mock_es_class.return_value = mock_es
        
        result = index_document('note', '888', {'title': 'Test'})
        
        self.assertFalse(result['success'])


class SearchQueryLoggingTests(TestCase):
    """Tests for search query logging"""
    
    def test_search_query_logging(self):
        """Test that search queries are logged"""
        with patch('elasticsearch_app.views.SearchService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.search_all.return_value = {
                'hits': [], 'total': 5, 'page': 1, 'per_page': 10, 'pages': 1
            }
            mock_service_class.return_value = mock_service
            
            initial_count = SearchQuery.objects.count()
            
            client = Client()
            response = client.get(
                reverse('elasticsearch_app:search'),
                {'q': 'logged query'}
            )
            
            self.assertEqual(SearchQuery.objects.count(), initial_count + 1)
