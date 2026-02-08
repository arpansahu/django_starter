"""
Elasticsearch Document Definitions

Defines the document schema for indexing in Elasticsearch.
"""
from elasticsearch_dsl import Document, Text, Keyword, Date, Integer, Boolean, Nested, InnerDoc
from django.conf import settings


# Index name prefix for this project
INDEX_PREFIX = getattr(settings, 'ELASTICSEARCH_INDEX_PREFIX', 'django_starter')


class TagInnerDoc(InnerDoc):
    """Inner document for tags"""
    name = Keyword()


class SearchableDocument(Document):
    """
    Base searchable document for general content indexing.
    """
    title = Text(analyzer='standard', fields={'raw': Keyword()})
    content = Text(analyzer='standard')
    summary = Text(analyzer='standard')
    doc_type = Keyword()
    author = Keyword()
    author_id = Integer()
    tags = Keyword(multi=True)
    category = Keyword()
    url = Keyword()
    created_at = Date()
    updated_at = Date()
    is_published = Boolean()
    view_count = Integer()
    
    class Index:
        name = f'{INDEX_PREFIX}_documents'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    def save(self, **kwargs):
        """Override save to set meta.id"""
        return super().save(**kwargs)


class NoteDocument(Document):
    """
    Document mapping for Notes app.
    """
    title = Text(analyzer='standard', fields={'raw': Keyword()})
    content = Text(analyzer='standard')
    slug = Keyword()
    author = Keyword()
    author_id = Integer()
    category = Keyword()
    category_id = Integer()
    tags = Keyword(multi=True)
    status = Keyword()
    is_pinned = Boolean()
    created_at = Date()
    updated_at = Date()
    
    class Index:
        name = f'{INDEX_PREFIX}_notes'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class UserDocument(Document):
    """
    Document mapping for User profiles.
    """
    username = Text(analyzer='standard', fields={'raw': Keyword()})
    email = Keyword()
    first_name = Text(analyzer='standard')
    last_name = Text(analyzer='standard')
    full_name = Text(analyzer='standard')
    is_active = Boolean()
    date_joined = Date()
    last_login = Date()
    
    class Index:
        name = f'{INDEX_PREFIX}_users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class LogDocument(Document):
    """
    Document mapping for application logs.
    """
    level = Keyword()
    message = Text(analyzer='standard')
    logger_name = Keyword()
    module = Keyword()
    function_name = Keyword()
    line_number = Integer()
    exception = Text()
    timestamp = Date()
    user_id = Integer()
    request_path = Keyword()
    request_method = Keyword()
    ip_address = Keyword()
    
    class Index:
        name = f'{INDEX_PREFIX}_logs'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


def create_all_indices():
    """
    Create all defined indices in Elasticsearch.
    """
    from .client import get_elasticsearch_client
    
    client = get_elasticsearch_client()
    
    # Initialize documents with client connection
    SearchableDocument.init(using=client)
    NoteDocument.init(using=client)
    UserDocument.init(using=client)
    LogDocument.init(using=client)
    
    return True


def delete_all_indices():
    """
    Delete all project indices from Elasticsearch.
    WARNING: This is destructive and cannot be undone!
    """
    from .client import get_elasticsearch_client
    
    client = get_elasticsearch_client()
    indices = [
        f'{INDEX_PREFIX}_documents',
        f'{INDEX_PREFIX}_notes',
        f'{INDEX_PREFIX}_users',
        f'{INDEX_PREFIX}_logs',
    ]
    
    for index in indices:
        try:
            client.indices.delete(index=index, ignore=[404])
        except Exception as e:
            print(f"Error deleting {index}: {e}")
    
    return True
