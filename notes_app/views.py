"""
Notes App Views - Complete Django Generic Class-Based Views Implementation

This module demonstrates ALL Django generic views:
- ListView
- DetailView  
- CreateView
- UpdateView
- DeleteView
- FormView
- TemplateView
- RedirectView
"""
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    FormView, TemplateView, RedirectView
)
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.db.models import Q, Count
from django.utils import timezone

from .models import Note, Category, Tag, Comment, Attachment
from .forms import NoteForm, CategoryForm, CommentForm, NoteFilterForm, AttachmentForm


# =============================================================================
# TEMPLATE VIEWS
# =============================================================================

class NotesHomeView(TemplateView):
    """Home page for notes app - demonstrates TemplateView"""
    template_name = 'notes_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_notes'] = Note.objects.count()
        context['total_categories'] = Category.objects.count()
        context['total_tags'] = Tag.objects.count()
        context['recent_notes'] = Note.objects.filter(
            status=Note.Status.ACTIVE
        ).select_related('author', 'category')[:5]
        context['popular_categories'] = Category.objects.annotate(
            notes_count=Count('notes')
        ).order_by('-notes_count')[:5]
        return context


class AboutNotesView(TemplateView):
    """About page - demonstrates TemplateView"""
    template_name = 'notes_app/about.html'
    extra_context = {
        'page_title': 'About Notes App',
        'features': [
            'Create and manage notes',
            'Organize with categories and tags',
            'Pin important notes',
            'Comment on notes',
            'Attach files',
        ]
    }


# =============================================================================
# LIST VIEWS
# =============================================================================

class NoteListView(ListView):
    """List all notes - demonstrates ListView with filtering and pagination"""
    model = Note
    template_name = 'notes_app/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10
    ordering = ['-is_pinned', '-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'category')
        
        # Filter by status (only show active notes to non-authors)
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True, status=Note.Status.ACTIVE)
        elif not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(author=self.request.user) |
                Q(is_public=True, status=Note.Status.ACTIVE)
            )
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(summary__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Priority filter
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = NoteFilterForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            notes_count=Count('notes')
        ).order_by('-notes_count')[:10]
        context['current_category'] = self.request.GET.get('category')
        context['current_tag'] = self.request.GET.get('tag')
        return context


class MyNotesListView(LoginRequiredMixin, ListView):
    """List current user's notes - demonstrates LoginRequiredMixin"""
    model = Note
    template_name = 'notes_app/my_notes.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        return Note.objects.filter(
            author=self.request.user
        ).select_related('category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['draft_count'] = self.get_queryset().filter(
            status=Note.Status.DRAFT
        ).count()
        context['active_count'] = self.get_queryset().filter(
            status=Note.Status.ACTIVE
        ).count()
        context['archived_count'] = self.get_queryset().filter(
            status=Note.Status.ARCHIVED
        ).count()
        return context


class CategoryListView(ListView):
    """List all categories - demonstrates ListView"""
    model = Category
    template_name = 'notes_app/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(
            notes_count=Count('notes')
        ).order_by('name')


class TagListView(ListView):
    """List all tags - demonstrates ListView"""
    model = Tag
    template_name = 'notes_app/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        return Tag.objects.annotate(
            notes_count=Count('notes')
        ).order_by('-notes_count')


class NotesByCategoryView(ListView):
    """List notes by category - demonstrates ListView with dynamic filtering"""
    model = Note
    template_name = 'notes_app/notes_by_category.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Note.objects.filter(
            category=self.category,
            status=Note.Status.ACTIVE
        ).select_related('author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class NotesByTagView(ListView):
    """List notes by tag - demonstrates ListView with M2M filtering"""
    model = Note
    template_name = 'notes_app/notes_by_tag.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Note.objects.filter(
            tags=self.tag,
            status=Note.Status.ACTIVE
        ).select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


# =============================================================================
# DETAIL VIEWS
# =============================================================================

class NoteDetailView(FormMixin, DetailView):
    """Note detail page - demonstrates DetailView with FormMixin for comments"""
    model = Note
    template_name = 'notes_app/note_detail.html'
    context_object_name = 'note'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = CommentForm
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'category')
        
        # Only show active/public notes to non-owners
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(author=self.request.user) |
                Q(status=Note.Status.ACTIVE)
            )
        return queryset.filter(is_public=True, status=Note.Status.ACTIVE)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            is_approved=True
        ).select_related('author')
        context['attachments'] = self.object.attachments.all()
        context['related_notes'] = Note.objects.filter(
            category=self.object.category,
            status=Note.Status.ACTIVE
        ).exclude(pk=self.object.pk)[:5]
        
        # Increment view count
        self.object.increment_view_count()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment submission"""
        if not request.user.is_authenticated:
            return redirect('account:login')
        
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.note = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect(self.object.get_absolute_url())
        
        return self.form_invalid(form)


class CategoryDetailView(DetailView):
    """Category detail page - demonstrates DetailView"""
    model = Category
    template_name = 'notes_app/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.filter(
            status=Note.Status.ACTIVE
        ).select_related('author')[:10]
        return context


# =============================================================================
# CREATE VIEWS
# =============================================================================

class NoteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new note - demonstrates CreateView with LoginRequiredMixin"""
    model = Note
    form_class = NoteForm
    template_name = 'notes_app/note_form.html'
    success_message = 'Note "%(title)s" created successfully!'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Note'
        context['submit_text'] = 'Create Note'
        return context


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new category - demonstrates CreateView"""
    model = Category
    form_class = CategoryForm
    template_name = 'notes_app/category_form.html'
    success_url = reverse_lazy('notes_app:category_list')
    success_message = 'Category "%(name)s" created successfully!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Category'
        context['submit_text'] = 'Create Category'
        return context


class QuickNoteCreateView(LoginRequiredMixin, CreateView):
    """Quick note creation - minimal fields"""
    model = Note
    fields = ['title', 'content']
    template_name = 'notes_app/quick_note_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        from django.utils.text import slugify
        import uuid
        form.instance.slug = f"{slugify(form.instance.title)}-{uuid.uuid4().hex[:8]}"
        messages.success(self.request, 'Quick note created!')
        return super().form_valid(form)


# =============================================================================
# UPDATE VIEWS
# =============================================================================

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Update a note - demonstrates UpdateView with permission check"""
    model = Note
    form_class = NoteForm
    template_name = 'notes_app/note_form.html'
    success_message = 'Note "%(title)s" updated successfully!'
    
    def test_func(self):
        """Only allow author or staff to edit"""
        note = self.get_object()
        return self.request.user == note.author or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit: {self.object.title}'
        context['submit_text'] = 'Update Note'
        return context


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update a category - demonstrates UpdateView"""
    model = Category
    form_class = CategoryForm
    template_name = 'notes_app/category_form.html'
    success_message = 'Category "%(name)s" updated successfully!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit: {self.object.name}'
        context['submit_text'] = 'Update Category'
        return context


class NotePublishView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Publish a note - demonstrates UpdateView for status change"""
    model = Note
    fields = []  # No form fields needed
    template_name = 'notes_app/note_confirm_publish.html'
    
    def test_func(self):
        note = self.get_object()
        return self.request.user == note.author or self.request.user.is_staff
    
    def form_valid(self, form):
        self.object.publish()
        messages.success(self.request, f'Note "{self.object.title}" published!')
        return redirect(self.object.get_absolute_url())


# =============================================================================
# DELETE VIEWS
# =============================================================================

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a note - demonstrates DeleteView with permission check"""
    model = Note
    template_name = 'notes_app/note_confirm_delete.html'
    success_url = reverse_lazy('notes_app:note_list')
    
    def test_func(self):
        """Only allow author or staff to delete"""
        note = self.get_object()
        return self.request.user == note.author or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Note "{self.get_object().title}" deleted!')
        return super().delete(request, *args, **kwargs)


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a category - demonstrates DeleteView"""
    model = Category
    template_name = 'notes_app/category_confirm_delete.html'
    success_url = reverse_lazy('notes_app:category_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Category "{self.get_object().name}" deleted!')
        return super().delete(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a comment - demonstrates DeleteView"""
    model = Comment
    template_name = 'notes_app/comment_confirm_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user == comment.author or
            self.request.user == comment.note.author or
            self.request.user.is_staff
        )
    
    def get_success_url(self):
        return self.object.note.get_absolute_url()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comment deleted!')
        return super().delete(request, *args, **kwargs)


# =============================================================================
# FORM VIEWS
# =============================================================================

class ContactFormView(FormView):
    """Contact form - demonstrates FormView"""
    template_name = 'notes_app/contact.html'
    form_class = CommentForm  # Reusing comment form for demo
    success_url = reverse_lazy('notes_app:contact_success')
    
    def form_valid(self, form):
        # In real app, would send email here
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        return context


class BulkActionFormView(LoginRequiredMixin, FormView):
    """Bulk action form - demonstrates FormView for batch operations"""
    template_name = 'notes_app/bulk_action.html'
    form_class = NoteFilterForm
    success_url = reverse_lazy('notes_app:my_notes')
    
    def form_valid(self, form):
        action = self.request.POST.get('action')
        note_ids = self.request.POST.getlist('note_ids')
        
        notes = Note.objects.filter(
            id__in=note_ids,
            author=self.request.user
        )
        
        if action == 'archive':
            notes.update(status=Note.Status.ARCHIVED)
            messages.success(self.request, f'{notes.count()} notes archived!')
        elif action == 'publish':
            notes.update(status=Note.Status.ACTIVE, published_at=timezone.now())
            messages.success(self.request, f'{notes.count()} notes published!')
        elif action == 'delete':
            count = notes.count()
            notes.delete()
            messages.success(self.request, f'{count} notes deleted!')
        
        return super().form_valid(form)


# =============================================================================
# REDIRECT VIEWS
# =============================================================================

class RandomNoteRedirectView(RedirectView):
    """Redirect to a random note - demonstrates RedirectView"""
    permanent = False
    query_string = True
    
    def get_redirect_url(self, *args, **kwargs):
        random_note = Note.objects.filter(
            status=Note.Status.ACTIVE,
            is_public=True
        ).order_by('?').first()
        
        if random_note:
            return random_note.get_absolute_url()
        return reverse('notes_app:note_list')


class LatestNoteRedirectView(RedirectView):
    """Redirect to latest note - demonstrates RedirectView"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        latest_note = Note.objects.filter(
            status=Note.Status.ACTIVE
        ).order_by('-created_at').first()
        
        if latest_note:
            return latest_note.get_absolute_url()
        return reverse('notes_app:note_list')


# =============================================================================
# AJAX / JSON VIEWS
# =============================================================================

class NoteTogglePinView(LoginRequiredMixin, UpdateView):
    """Toggle pin status via AJAX - demonstrates UpdateView for AJAX"""
    model = Note
    fields = []
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.author != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        self.object.is_pinned = not self.object.is_pinned
        self.object.save(update_fields=['is_pinned'])
        
        return JsonResponse({
            'success': True,
            'is_pinned': self.object.is_pinned,
            'message': 'Note pinned!' if self.object.is_pinned else 'Note unpinned!'
        })


class NoteArchiveView(LoginRequiredMixin, UpdateView):
    """Archive a note via AJAX"""
    model = Note
    fields = []
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.author != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        self.object.archive()
        
        return JsonResponse({
            'success': True,
            'status': self.object.status,
            'message': 'Note archived!'
        })
