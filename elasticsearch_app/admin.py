"""
Elasticsearch Admin Configuration
"""
from django.contrib import admin
from .models import IndexedDocument, SearchQuery, SearchSynonym


@admin.register(IndexedDocument)
class IndexedDocumentAdmin(admin.ModelAdmin):
    list_display = ['doc_type', 'source_id', 'es_index', 'status', 'indexed_at', 'updated_at']
    list_filter = ['doc_type', 'status', 'es_index']
    search_fields = ['source_id', 'es_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'index', 'results_count', 'response_time_ms', 'created_at']
    list_filter = ['index', 'created_at']
    search_fields = ['query', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # Search queries are auto-generated


@admin.register(SearchSynonym)
class SearchSynonymAdmin(admin.ModelAdmin):
    list_display = ['term', 'synonyms', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['term', 'synonyms']
    readonly_fields = ['created_at', 'updated_at']
