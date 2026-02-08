"""
Elasticsearch App Views

Views for search UI and Elasticsearch management.
"""
import time
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from .client import get_elasticsearch_client, check_elasticsearch_connection, get_cluster_health, get_index_stats
from .search import SearchService
from .models import SearchQuery
from .documents import create_all_indices, delete_all_indices, INDEX_PREFIX


class ElasticsearchDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard showing Elasticsearch status and management options.
    """
    template_name = 'elasticsearch_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get connection status
        context['connection'] = check_elasticsearch_connection()
        
        # Get cluster health
        if context['connection']['connected']:
            context['health'] = get_cluster_health()
            context['indices'] = get_index_stats()
        
        # Recent search queries
        context['recent_queries'] = SearchQuery.objects.all()[:10]
        
        return context


class SearchView(TemplateView):
    """
    Main search interface.
    """
    template_name = 'elasticsearch_app/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get('q', '').strip()
        index_filter = self.request.GET.get('index', '')
        page = int(self.request.GET.get('page', 1))
        
        context['query'] = query
        context['index_filter'] = index_filter
        context['results'] = None
        
        if query:
            start_time = time.time()
            
            try:
                search_service = SearchService()
                
                if index_filter == 'notes':
                    results = search_service.search_notes(query, page=page)
                elif index_filter == 'users':
                    results = search_service.search_users(query, page=page)
                elif index_filter == 'logs':
                    results = search_service.search_logs(query, page=page)
                else:
                    results = search_service.search_all(query, page=page)
                
                context['results'] = results
                
                # Log the search query
                response_time = int((time.time() - start_time) * 1000)
                SearchQuery.objects.create(
                    query=query,
                    user=self.request.user if self.request.user.is_authenticated else None,
                    index=index_filter or 'all',
                    results_count=results.get('total', 0),
                    response_time_ms=response_time,
                    ip_address=self.request.META.get('REMOTE_ADDR'),
                    user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                
            except Exception as e:
                context['error'] = str(e)
        
        return context


class SearchAPIView(View):
    """
    API endpoint for AJAX search.
    """
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        index_filter = request.GET.get('index', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
        
        try:
            search_service = SearchService()
            
            if index_filter == 'notes':
                results = search_service.search_notes(query, page=page, per_page=per_page)
            elif index_filter == 'users':
                results = search_service.search_users(query, page=page, per_page=per_page)
            elif index_filter == 'logs':
                results = search_service.search_logs(query, page=page, per_page=per_page)
            else:
                results = search_service.search_all(query, page=page, per_page=per_page)
            
            return JsonResponse(results)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SuggestAPIView(View):
    """
    API endpoint for search suggestions/autocomplete.
    """
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        try:
            search_service = SearchService()
            suggestions = search_service.suggest(query)
            return JsonResponse({'suggestions': suggestions})
        except Exception as e:
            return JsonResponse({'suggestions': [], 'error': str(e)})


class IndexManagementView(LoginRequiredMixin, View):
    """
    View for managing Elasticsearch indices.
    """
    raise_exception = True  # Return 403 instead of redirect for AJAX
    
    def handle_no_permission(self):
        """Return JSON error for AJAX requests."""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           self.request.content_type == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        return super().handle_no_permission()
    
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'create_indices':
            try:
                create_all_indices()
                return JsonResponse({'success': True, 'message': 'Indices created successfully'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        elif action == 'delete_indices':
            try:
                delete_all_indices()
                return JsonResponse({'success': True, 'message': 'Indices deleted successfully'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        elif action == 'reindex':
            try:
                # Trigger reindex task
                from .tasks import reindex_all_documents
                reindex_all_documents.delay()
                return JsonResponse({'success': True, 'message': 'Reindex task started'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Unknown action'})


class ClusterHealthAPIView(View):
    """
    API endpoint for cluster health.
    """
    
    def get(self, request):
        health = get_cluster_health()
        return JsonResponse(health)


class IndicesAPIView(View):
    """
    API endpoint for indices information.
    """
    
    def get(self, request):
        indices = get_index_stats()
        return JsonResponse({'indices': indices})


class SearchAnalyticsView(LoginRequiredMixin, TemplateView):
    """
    View for search analytics.
    """
    template_name = 'elasticsearch_app/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top search queries
        from django.db.models import Count
        context['top_queries'] = (
            SearchQuery.objects
            .values('query')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
        
        # Recent queries
        context['recent_queries'] = SearchQuery.objects.all()[:50]
        
        # Zero result queries
        context['zero_result_queries'] = (
            SearchQuery.objects
            .filter(results_count=0)
            .values('query')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
        
        # Average response time
        from django.db.models import Avg
        context['avg_response_time'] = (
            SearchQuery.objects.aggregate(avg_time=Avg('response_time_ms'))['avg_time']
        )
        
        return context
