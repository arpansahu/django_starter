"""
Elasticsearch App Configuration
"""
from django.apps import AppConfig


class ElasticsearchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elasticsearch_app'
    verbose_name = 'Elasticsearch Search'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import elasticsearch_app.signals  # noqa
        except ImportError:
            pass
