"""
Forms for Commands App
"""
from django import forms
from django.core.management import get_commands
import json
from .models import ScheduledTask, TaskPriority


class ScheduledTaskForm(forms.ModelForm):
    """Form for creating/editing scheduled tasks"""
    
    class Meta:
        model = ScheduledTask
        fields = [
            'name', 'command', 'arguments', 'schedule',
            'is_active', 'priority', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'command': forms.Select(attrs={'class': 'form-select'}),
            'arguments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '{"args": [], "kwargs": {}}'
            }),
            'schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '*/5 * * * * (every 5 minutes)'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate command choices
        commands = sorted(get_commands().keys())
        self.fields['command'] = forms.ChoiceField(
            choices=[(cmd, cmd) for cmd in commands],
            widget=forms.Select(attrs={'class': 'form-select'})
        )
    
    def clean_arguments(self):
        arguments = self.cleaned_data.get('arguments')
        if arguments:
            try:
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
            except json.JSONDecodeError:
                raise forms.ValidationError('Arguments must be valid JSON')
        return arguments or {}


class RunCommandForm(forms.Form):
    """Form for running a command manually"""
    command = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    arguments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '{"key": "value"}'
        }),
        help_text='JSON format arguments'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        commands = sorted(get_commands().keys())
        self.fields['command'].choices = [(cmd, cmd) for cmd in commands]
    
    def clean_arguments(self):
        arguments = self.cleaned_data.get('arguments')
        if arguments:
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                raise forms.ValidationError('Arguments must be valid JSON')
        return arguments or {}


class DataImportForm(forms.Form):
    """Form for importing data"""
    source_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    model = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'app.Model'
        })
    )
    format = forms.ChoiceField(
        choices=[
            ('auto', 'Auto-detect'),
            ('csv', 'CSV'),
            ('json', 'JSON'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    dry_run = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Validate without actually importing'
    )


class DataExportForm(forms.Form):
    """Form for exporting data"""
    model = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'app.Model'
        })
    )
    format = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('json', 'JSON'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fields = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'field1, field2, field3 (leave empty for all)'
        })
    )
    filter_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': '{"is_active": true}'
        }),
        help_text='JSON filter expression'
    )
