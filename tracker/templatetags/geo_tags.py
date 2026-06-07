from django import template

from tracker.utils.geolocation import is_private_ip, location_label

register = template.Library()


@register.filter
def private_ip(ip):
    return is_private_ip(ip)


@register.filter
def geo_location(city, arg):
    """Usage: {{ event.city|geo_location:event }} where event has country and ip."""
    country = ''
    ip = None
    if hasattr(arg, 'country'):
        country = arg.country
        ip = getattr(arg, 'ip_address', None) or getattr(arg, 'source_ip', None)
    elif isinstance(arg, dict):
        country = arg.get('country', '')
        ip = arg.get('ip')
    return location_label(city, country, ip)
