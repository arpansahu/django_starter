"""
Elasticsearch Client Configuration

Provides singleton Elasticsearch client and utility functions.
"""
import os
from elasticsearch import Elasticsearch
from django.conf import settings


# Module-level client instance
_es_client = None


def get_elasticsearch_client():
    """
    Get Elasticsearch client instance (singleton).
    
    Returns:
        Elasticsearch: Configured Elasticsearch client
    """
    global _es_client
    
    if _es_client is not None:
        return _es_client
    
    es_host = getattr(settings, 'ELASTICSEARCH_HOST', None) or os.getenv('ELASTICSEARCH_HOST', 'https://elasticsearch.arpansahu.space')
    es_user = getattr(settings, 'ELASTICSEARCH_USER', None) or os.getenv('ELASTICSEARCH_USER', 'elastic')
    es_password = getattr(settings, 'ELASTICSEARCH_PASSWORD', None) or os.getenv('ELASTICSEARCH_PASSWORD', '')
    
    # Create client with http_auth (for elasticsearch-py 7.x)
    if es_user and es_password:
        _es_client = Elasticsearch(
            hosts=[es_host],
            http_auth=(es_user, es_password),
            verify_certs=True,
            request_timeout=30,
        )
    else:
        # No auth
        _es_client = Elasticsearch(
            hosts=[es_host],
            verify_certs=True,
            request_timeout=30,
        )
    
    return _es_client


def reset_elasticsearch_client():
    """Reset the cached client (useful for testing or config changes)."""
    global _es_client
    _es_client = None


def check_elasticsearch_connection():
    """
    Check if Elasticsearch is reachable.
    
    Returns:
        dict: Connection status with cluster info or error message
    """
    try:
        client = get_elasticsearch_client()
        info = client.info()
        return {
            'connected': True,
            'cluster_name': info['cluster_name'],
            'version': info['version']['number'],
            'tagline': info['tagline']
        }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }


def get_cluster_health():
    """
    Get Elasticsearch cluster health.
    
    Returns:
        dict: Cluster health information
    """
    try:
        client = get_elasticsearch_client()
        health = client.cluster.health()
        return {
            'status': health['status'],
            'cluster_name': health['cluster_name'],
            'number_of_nodes': health['number_of_nodes'],
            'number_of_data_nodes': health['number_of_data_nodes'],
            'active_shards': health['active_shards'],
            'active_primary_shards': health['active_primary_shards'],
        }
    except Exception as e:
        return {
            'status': 'unavailable',
            'error': str(e)
        }


def get_index_stats():
    """
    Get statistics for all indices.
    
    Returns:
        list: List of index information
    """
    try:
        client = get_elasticsearch_client()
        indices = client.cat.indices(format='json')
        return indices
    except Exception as e:
        return []
