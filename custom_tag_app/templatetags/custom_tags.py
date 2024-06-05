from django import template

register = template.Library()


@register.filter
def calculate_percentage(pages, read, *args):
    return ((read/pages) * 100)
