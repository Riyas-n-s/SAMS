from django import template

register = template.Library()

@register.filter
def dictkey(d, key):
    """Returns the value of the dictionary by key"""
    return d.get(key)
