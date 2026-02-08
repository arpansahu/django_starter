"""
Elasticsearch App Models

Models for tracking indexed documents and search analytics.
"""
from django.db import models
from django.conf import settings


class IndexedDocument(models.Model):
    """
    Track documents that have been indexed in Elasticsearch.
    """
    DOCUMENT_TYPES = [
        ('note', 'Note'),
        ('user', 'User'),
        ('log', 'Log'),
        ('custom', 'Custom Document'),
    ]
    
    STATUS_CHOICES = [
        ('indexed', 'Indexed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted'),
    ]
    
    # Document identification
    doc_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    source_id = models.CharField(max_length=255, help_text="ID in the source system")
    es_id = models.CharField(max_length=255, blank=True, null=True, help_text="Elasticsearch document ID")
    es_index = models.CharField(max_length=255, help_text="Elasticsearch index name")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    indexed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Indexed Document'
        verbose_name_plural = 'Indexed Documents'
        unique_together = ['doc_type', 'source_id']
        indexes = [
            models.Index(fields=['doc_type', 'status']),
            models.Index(fields=['es_index']),
        ]
    
    def __str__(self):
        return f"{self.doc_type}:{self.source_id} ({self.status})"


class SearchQuery(models.Model):
    """
    Log search queries for analytics.
    """
    query = models.CharField(max_length=500)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    index = models.CharField(max_length=255, blank=True, null=True)
    filters = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(default=0, help_text="Response time in milliseconds")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'"{self.query}" ({self.results_count} results)'


class SearchSynonym(models.Model):
    """
    Store custom synonyms for search.
    """
    term = models.CharField(max_length=100, unique=True)
    synonyms = models.TextField(help_text="Comma-separated list of synonyms")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Search Synonym'
        verbose_name_plural = 'Search Synonyms'
    
    def __str__(self):
        return f"{self.term}: {self.synonyms[:50]}..."
    
    def get_synonyms_list(self):
        return [s.strip() for s in self.synonyms.split(',')]
