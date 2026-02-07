"""
Notes App Models - Demonstrates Django Models with various field types
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """Category for organizing notes"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color
    icon = models.CharField(max_length=50, default='folder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('notes_app:category_detail', kwargs={'slug': self.slug})
    
    @property
    def note_count(self):
        return self.notes.count()


class Tag(models.Model):
    """Tags for notes"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Note(models.Model):
    """Main Note model - the core of the app"""
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'
    
    # Core fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True)
    
    # Relationships
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    
    # Status fields
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Boolean flags
    is_pinned = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('notes_app:note_detail', kwargs={'slug': self.slug})
    
    def publish(self):
        """Publish the note"""
        self.status = self.Status.ACTIVE
        self.published_at = timezone.now()
        self.save()
    
    def archive(self):
        """Archive the note"""
        self.status = self.Status.ARCHIVED
        self.save()
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    @property
    def is_published(self):
        return self.status == self.Status.ACTIVE
    
    @property
    def word_count(self):
        return len(self.content.split())


class Comment(models.Model):
    """Comments on notes"""
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='note_comments'
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author} on {self.note}'


class Attachment(models.Model):
    """File attachments for notes"""
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='note_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            if not self.filename:
                self.filename = self.file.name
        super().save(*args, **kwargs)
