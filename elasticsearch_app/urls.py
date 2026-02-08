"""
Elasticsearch App URLs
"""
from django.urls import path
from . import views

app_name = 'elasticsearch_app'

urlpatterns = [
    # Dashboard
    path('', views.ElasticsearchDashboardView.as_view(), name='dashboard'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    path('analytics/', views.SearchAnalyticsView.as_view(), name='analytics'),
    
    # API endpoints
    path('api/search/', views.SearchAPIView.as_view(), name='api_search'),
    path('api/suggest/', views.SuggestAPIView.as_view(), name='api_suggest'),
    path('api/health/', views.ClusterHealthAPIView.as_view(), name='api_health'),
    path('api/indices/', views.IndicesAPIView.as_view(), name='api_indices'),
    
    # Management
    path('manage/', views.IndexManagementView.as_view(), name='manage'),
]
