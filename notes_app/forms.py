"""
Notes App Forms - Django forms for CRUD operations
"""
from django import forms
from django.utils.text import slugify
from .models import Note, Category, Tag, Comment, Attachment


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Icon name (e.g., folder, star)'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError('Category name must be at least 2 characters.')
        return name
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class TagForm(forms.ModelForm):
    """Form for creating tags"""
    
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag name'
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class NoteForm(forms.ModelForm):
    """Form for creating/editing notes"""
    
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas'
        }),
        help_text='Enter tags separated by commas (e.g., python, django, web)'
    )
    
    class Meta:
        model = Note
        fields = [
            'title', 'content', 'summary', 'category',
            'priority', 'status', 'is_pinned', 'is_public', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Note title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your note content here...'
            }),
            'summary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial tags if editing existing note
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')
        return title
    
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 10:
            raise forms.ValidationError('Content must be at least 10 characters.')
        return content
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Generate slug if not exists
        if not instance.slug:
            base_slug = slugify(instance.title)
            slug = base_slug
            counter = 1
            while Note.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            instance.slug = slug
        
        if commit:
            instance.save()
            
            # Handle tags
            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                tags = []
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(
                        name=name,
                        defaults={'slug': slugify(name)}
                    )
                    tags.append(tag)
                instance.tags.set(tags)
            else:
                instance.tags.clear()
        
        return instance


class NoteFilterForm(forms.Form):
    """Form for filtering notes list"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search notes...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Note.Priority.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Note.Status.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class CommentForm(forms.ModelForm):
    """Form for adding comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters.')
        return content


class AttachmentForm(forms.ModelForm):
    """Form for uploading attachments"""
    
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.gif'
            }),
        }
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            # Max 10MB
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB.')
            
            # Check allowed extensions
            allowed_extensions = [
                'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif'
            ]
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'
                )
        return file
