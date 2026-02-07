"""
Notes App URLs
"""
from django.urls import path
from . import views

app_name = 'notes_app'

urlpatterns = [
    # Home and static pages
    path('', views.NotesHomeView.as_view(), name='home'),
    path('about/', views.AboutNotesView.as_view(), name='about'),
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('contact/success/', views.AboutNotesView.as_view(), name='contact_success'),
    
    # Note list views
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('my-notes/', views.MyNotesListView.as_view(), name='my_notes'),
    path('notes/bulk-action/', views.BulkActionFormView.as_view(), name='bulk_action'),
    
    # Note CRUD
    path('notes/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/quick/', views.QuickNoteCreateView.as_view(), name='quick_note'),
    path('notes/<slug:slug>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('notes/<slug:slug>/edit/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<slug:slug>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('notes/<slug:slug>/publish/', views.NotePublishView.as_view(), name='note_publish'),
    
    # AJAX endpoints
    path('notes/<int:pk>/toggle-pin/', views.NoteTogglePinView.as_view(), name='toggle_pin'),
    path('notes/<int:pk>/archive/', views.NoteArchiveView.as_view(), name='archive_note'),
    
    # Category views
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/<slug:slug>/notes/', views.NotesByCategoryView.as_view(), name='notes_by_category'),
    
    # Tag views
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/', views.NotesByTagView.as_view(), name='notes_by_tag'),
    
    # Comment deletion
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # Redirect views
    path('random/', views.RandomNoteRedirectView.as_view(), name='random_note'),
    path('latest/', views.LatestNoteRedirectView.as_view(), name='latest_note'),
]
