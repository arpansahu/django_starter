from django.contrib import admin
from .models import Note, Category, Tag, Comment, Attachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'note_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    
    def note_count(self, obj):
        return obj.notes.count()
    note_count.short_description = 'Notes'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'note_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def note_count(self, obj):
        return obj.notes.count()
    note_count.short_description = 'Notes'


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'priority', 'is_pinned', 'created_at']
    list_filter = ['status', 'priority', 'is_pinned', 'is_public', 'category', 'created_at']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'published_at']
    inlines = [CommentInline, AttachmentInline]
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'summary')
        }),
        ('Relationships', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'is_pinned', 'is_public', 'allow_comments')
        }),
        ('Metadata', {
            'fields': ('view_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_published', 'make_archived', 'toggle_pin']
    
    def make_published(self, request, queryset):
        queryset.update(status=Note.Status.ACTIVE)
    make_published.short_description = 'Mark selected notes as published'
    
    def make_archived(self, request, queryset):
        queryset.update(status=Note.Status.ARCHIVED)
    make_archived.short_description = 'Archive selected notes'
    
    def toggle_pin(self, request, queryset):
        for note in queryset:
            note.is_pinned = not note.is_pinned
            note.save(update_fields=['is_pinned'])
    toggle_pin.short_description = 'Toggle pin status'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['note', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'note__title']
    raw_id_fields = ['note', 'author']
    
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Approve selected comments'
    
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
    reject_comments.short_description = 'Reject selected comments'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'note', 'file_size', 'mime_type', 'uploaded_at']
    list_filter = ['mime_type', 'uploaded_at']
    search_fields = ['filename', 'note__title']
    raw_id_fields = ['note']
