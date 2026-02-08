"""
Elasticsearch Celery Tasks

Background tasks for indexing and maintenance.
"""
from celery import shared_task
from django.utils import timezone


@shared_task(bind=True)
def index_document(self, doc_type, source_id, data):
    """
    Index a single document in Elasticsearch.
    
    Args:
        doc_type: Type of document (note, user, log, etc.)
        source_id: ID from the source system
        data: Document data to index
    """
    from .client import get_elasticsearch_client
    from .documents import INDEX_PREFIX
    from .models import IndexedDocument
    
    client = get_elasticsearch_client()
    index_name = f'{INDEX_PREFIX}_{doc_type}s'
    
    try:
        # Index the document
        response = client.index(
            index=index_name,
            id=f'{doc_type}_{source_id}',
            body=data
        )
        
        # Update or create tracking record
        IndexedDocument.objects.update_or_create(
            doc_type=doc_type,
            source_id=str(source_id),
            defaults={
                'es_id': response['_id'],
                'es_index': index_name,
                'status': 'indexed',
                'indexed_at': timezone.now(),
                'error_message': None
            }
        )
        
        return {'success': True, 'es_id': response['_id']}
        
    except Exception as e:
        # Log the error
        IndexedDocument.objects.update_or_create(
            doc_type=doc_type,
            source_id=str(source_id),
            defaults={
                'es_index': index_name,
                'status': 'failed',
                'error_message': str(e)
            }
        )
        return {'success': False, 'error': str(e)}


@shared_task(bind=True)
def delete_document(self, doc_type, source_id):
    """
    Delete a document from Elasticsearch.
    """
    from .client import get_elasticsearch_client
    from .documents import INDEX_PREFIX
    from .models import IndexedDocument
    
    client = get_elasticsearch_client()
    index_name = f'{INDEX_PREFIX}_{doc_type}s'
    
    try:
        client.delete(
            index=index_name,
            id=f'{doc_type}_{source_id}',
            ignore=[404]
        )
        
        # Update tracking record
        IndexedDocument.objects.filter(
            doc_type=doc_type,
            source_id=str(source_id)
        ).update(status='deleted')
        
        return {'success': True}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


@shared_task(bind=True)
def reindex_all_documents(self):
    """
    Reindex all documents from Django models to Elasticsearch.
    """
    from .client import get_elasticsearch_client
    from .documents import INDEX_PREFIX, NoteDocument, UserDocument
    from django.contrib.auth import get_user_model
    
    client = get_elasticsearch_client()
    User = get_user_model()
    
    indexed_count = 0
    error_count = 0
    
    # Index all users
    for user in User.objects.all():
        try:
            data = {
                'username': user.username,
                'email': user.email,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'full_name': f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            
            index_document.delay('user', user.id, data)
            indexed_count += 1
            
        except Exception as e:
            error_count += 1
    
    # Try to index notes if notes_app exists
    try:
        from notes_app.models import Note
        
        for note in Note.objects.all():
            try:
                data = {
                    'title': note.title,
                    'content': note.content,
                    'slug': note.slug,
                    'author': note.author.username if note.author else None,
                    'author_id': note.author.id if note.author else None,
                    'category': note.category.name if hasattr(note, 'category') and note.category else None,
                    'category_id': note.category.id if hasattr(note, 'category') and note.category else None,
                    'status': getattr(note, 'status', 'active'),
                    'is_pinned': getattr(note, 'is_pinned', False),
                    'created_at': note.created_at.isoformat() if note.created_at else None,
                    'updated_at': note.updated_at.isoformat() if note.updated_at else None,
                }
                
                # Add tags if available
                if hasattr(note, 'tags'):
                    data['tags'] = [tag.name for tag in note.tags.all()]
                
                index_document.delay('note', note.id, data)
                indexed_count += 1
                
            except Exception as e:
                error_count += 1
                
    except ImportError:
        pass  # notes_app not installed
    
    return {
        'success': True,
        'indexed_count': indexed_count,
        'error_count': error_count
    }


@shared_task
def cleanup_old_search_queries(days=30):
    """
    Remove old search query logs.
    """
    from .models import SearchQuery
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count = SearchQuery.objects.filter(created_at__lt=cutoff_date).delete()[0]
    
    return {'deleted_count': deleted_count}


@shared_task
def sync_index_status():
    """
    Sync index status between Django and Elasticsearch.
    """
    from .client import get_elasticsearch_client
    from .models import IndexedDocument
    
    client = get_elasticsearch_client()
    
    # Check each indexed document
    for doc in IndexedDocument.objects.filter(status='indexed'):
        try:
            exists = client.exists(index=doc.es_index, id=doc.es_id)
            if not exists:
                doc.status = 'deleted'
                doc.save()
        except Exception:
            pass
    
    return {'success': True}
