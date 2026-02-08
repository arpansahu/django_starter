"""
Elasticsearch Search Service

Provides search functionality across indexed documents.
"""
from elasticsearch_dsl import Search, Q
from .client import get_elasticsearch_client
from .documents import INDEX_PREFIX


class SearchService:
    """
    Service class for performing searches across Elasticsearch indices.
    """
    
    def __init__(self):
        self.client = get_elasticsearch_client()
    
    def search_all(self, query_string, page=1, per_page=10, doc_type=None):
        """
        Search across all indices.
        
        Args:
            query_string: The search query
            page: Page number (1-indexed)
            per_page: Results per page
            doc_type: Optional filter by document type
            
        Returns:
            dict: Search results with metadata
        """
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build search across all project indices
        s = Search(using=self.client, index=f'{INDEX_PREFIX}_*')
        
        if query_string:
            # Multi-match query across multiple fields
            s = s.query(
                'multi_match',
                query=query_string,
                fields=['title^3', 'content^2', 'summary', 'message', 'username', 'email'],
                type='best_fields',
                fuzziness='AUTO'
            )
        
        if doc_type:
            s = s.filter('term', doc_type=doc_type)
        
        # Add pagination
        s = s[offset:offset + per_page]
        
        # Add highlighting
        s = s.highlight('title', 'content', 'message', fragment_size=150)
        
        # Execute search
        response = s.execute()
        
        return self._format_response(response, page, per_page)
    
    def search_notes(self, query_string, page=1, per_page=10, filters=None):
        """
        Search notes index.
        
        Args:
            query_string: The search query
            page: Page number
            per_page: Results per page
            filters: Optional dict of filters (category, status, tags)
            
        Returns:
            dict: Search results
        """
        offset = (page - 1) * per_page
        
        s = Search(using=self.client, index=f'{INDEX_PREFIX}_notes')
        
        if query_string:
            s = s.query(
                'multi_match',
                query=query_string,
                fields=['title^3', 'content^2'],
                type='best_fields',
                fuzziness='AUTO'
            )
        
        # Apply filters
        if filters:
            if filters.get('category'):
                s = s.filter('term', category=filters['category'])
            if filters.get('status'):
                s = s.filter('term', status=filters['status'])
            if filters.get('tags'):
                s = s.filter('terms', tags=filters['tags'])
            if filters.get('author_id'):
                s = s.filter('term', author_id=filters['author_id'])
        
        s = s[offset:offset + per_page]
        s = s.highlight('title', 'content', fragment_size=150)
        
        response = s.execute()
        return self._format_response(response, page, per_page)
    
    def search_users(self, query_string, page=1, per_page=10):
        """
        Search users index.
        """
        offset = (page - 1) * per_page
        
        s = Search(using=self.client, index=f'{INDEX_PREFIX}_users')
        
        if query_string:
            s = s.query(
                'multi_match',
                query=query_string,
                fields=['username^3', 'email^2', 'first_name', 'last_name', 'full_name'],
                type='best_fields',
                fuzziness='AUTO'
            )
        
        s = s[offset:offset + per_page]
        s = s.highlight('username', 'email', 'full_name', fragment_size=100)
        
        response = s.execute()
        return self._format_response(response, page, per_page)
    
    def search_logs(self, query_string, page=1, per_page=20, filters=None):
        """
        Search logs index.
        """
        offset = (page - 1) * per_page
        
        s = Search(using=self.client, index=f'{INDEX_PREFIX}_logs')
        
        if query_string:
            s = s.query(
                'multi_match',
                query=query_string,
                fields=['message^2', 'exception', 'logger_name'],
                type='best_fields'
            )
        
        # Apply filters
        if filters:
            if filters.get('level'):
                s = s.filter('term', level=filters['level'])
            if filters.get('module'):
                s = s.filter('term', module=filters['module'])
            if filters.get('date_from'):
                s = s.filter('range', timestamp={'gte': filters['date_from']})
            if filters.get('date_to'):
                s = s.filter('range', timestamp={'lte': filters['date_to']})
        
        # Sort by timestamp descending
        s = s.sort('-timestamp')
        s = s[offset:offset + per_page]
        
        response = s.execute()
        return self._format_response(response, page, per_page)
    
    def suggest(self, query_string, field='title', index=None):
        """
        Get search suggestions (autocomplete).
        """
        if index is None:
            index = f'{INDEX_PREFIX}_*'
        
        s = Search(using=self.client, index=index)
        s = s.suggest(
            'suggestions',
            query_string,
            completion={
                'field': f'{field}.suggest',
                'fuzzy': {'fuzziness': 'AUTO'},
                'size': 5
            }
        )
        
        response = s.execute()
        
        suggestions = []
        if hasattr(response, 'suggest') and 'suggestions' in response.suggest:
            for option in response.suggest.suggestions[0].options:
                suggestions.append(option.text)
        
        return suggestions
    
    def aggregate_by_field(self, field, index=None, size=10):
        """
        Get aggregations/facets for a field.
        """
        if index is None:
            index = f'{INDEX_PREFIX}_*'
        
        s = Search(using=self.client, index=index)
        s.aggs.bucket('by_field', 'terms', field=field, size=size)
        s = s[:0]  # Don't return documents
        
        response = s.execute()
        
        buckets = []
        if hasattr(response.aggregations, 'by_field'):
            for bucket in response.aggregations.by_field.buckets:
                buckets.append({
                    'key': bucket.key,
                    'count': bucket.doc_count
                })
        
        return buckets
    
    def _format_response(self, response, page, per_page):
        """
        Format Elasticsearch response to consistent structure.
        """
        hits = []
        for hit in response:
            item = {
                'id': hit.meta.id,
                'index': hit.meta.index,
                'score': hit.meta.score,
            }
            
            # Add document fields
            for field in hit.to_dict():
                item[field] = hit.to_dict()[field]
            
            # Add highlights if present
            if hasattr(hit.meta, 'highlight'):
                item['highlights'] = dict(hit.meta.highlight)
            
            hits.append(item)
        
        return {
            'hits': hits,
            'total': response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total,
            'page': page,
            'per_page': per_page,
            'pages': (response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total) // per_page + 1
        }
