"""
IP geolocation utilities.
Resolves country, city, ISP, and ASN from an IP address.
"""
import json
import urllib.error
import urllib.request
from functools import lru_cache
from typing import Any, Dict, Optional, Type


PRIVATE_IP_PREFIXES = (
    '127.', '10.', '192.168.', '172.16.', '172.17.', '172.18.',
    '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
    '172.29.', '172.30.', '172.31.', '::1', 'fc', 'fd',
)

GEO_FIELDS = ('country', 'city', 'isp', 'asn', 'latitude', 'longitude')


def is_private_ip(ip: Optional[str]) -> bool:
    if not ip:
        return True
    normalized = str(ip).lower()
    return normalized == 'localhost' or any(normalized.startswith(prefix) for prefix in PRIVATE_IP_PREFIXES)


def location_label(city: str, country: str, ip: Optional[str] = None) -> str:
    """Human-readable location string for templates."""
    if is_private_ip(ip):
        return 'Local / Private network'
    parts = [part for part in (city, country) if part]
    return ', '.join(parts) if parts else 'Unknown'


@lru_cache(maxsize=512)
def lookup_ip(ip: str) -> Dict[str, Any]:
    """Look up geolocation for a public IP. Tries HTTPS providers in order."""
    if is_private_ip(ip):
        return {}

    for provider in (_lookup_ipwhois, _lookup_ip_api):
        geo = provider(ip)
        if geo.get('latitude') is not None and geo.get('longitude') is not None:
            return geo

    return {}


def _fetch_json(url: str) -> Dict[str, Any]:
    request = urllib.request.Request(url, headers={'User-Agent': 'fyp-honeypot/1.0'})
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode())


def _lookup_ipwhois(ip: str) -> Dict[str, Any]:
    """Primary provider — HTTPS, works on Render/production."""
    try:
        data = _fetch_json(f'https://ipwho.is/{ip}')
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError):
        return {}

    if not data.get('success'):
        return {}

    connection = data.get('connection') or {}
    asn = connection.get('asn')
    return {
        'country': data.get('country', '') or '',
        'city': data.get('city', '') or '',
        'isp': connection.get('isp', '') or '',
        'asn': f'AS{asn}' if asn else (connection.get('org', '') or ''),
        'latitude': float(data['latitude']) if data.get('latitude') is not None else None,
        'longitude': float(data['longitude']) if data.get('longitude') is not None else None,
    }


def _lookup_ip_api(ip: str) -> Dict[str, Any]:
    """Fallback provider — HTTP only on free tier."""
    try:
        data = _fetch_json(
            f'http://ip-api.com/json/{ip}?fields=status,country,city,isp,as,lat,lon'
        )
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError):
        return {}

    if data.get('status') != 'success':
        return {}

    lat = data.get('lat')
    lon = data.get('lon')
    return {
        'country': data.get('country', '') or '',
        'city': data.get('city', '') or '',
        'isp': data.get('isp', '') or '',
        'asn': data.get('as', '') or '',
        'latitude': float(lat) if lat is not None else None,
        'longitude': float(lon) if lon is not None else None,
    }


def get_geo_for_ip(ip: str) -> Dict[str, Any]:
    """
    Resolve geolocation for an IP.
    Reuses cached DB records with coordinates, otherwise performs external lookup.
    """
    if not ip or is_private_ip(ip):
        return {}

    from ..models import AccessLog, BotSignal

    for model, field in ((AccessLog, 'ip_address'), (BotSignal, 'source_ip')):
        existing = model.objects.filter(
            **{field: ip},
            latitude__isnull=False,
            longitude__isnull=False,
        ).order_by('-timestamp').values(
            'country', 'city', 'isp', 'asn', 'latitude', 'longitude',
        ).first()

        if existing:
            geo = {key: existing.get(key, '') or '' for key in ('country', 'city', 'isp', 'asn')}
            geo['latitude'] = existing.get('latitude')
            geo['longitude'] = existing.get('longitude')
            return geo

    return lookup_ip(ip)


def apply_geo_to_instance(instance: Any, ip: Optional[str]) -> None:
    """Populate geolocation fields on a model instance from an IP."""
    geo = get_geo_for_ip(ip) if ip else {}
    for field in GEO_FIELDS:
        default = '' if field in ('country', 'city', 'isp', 'asn') else None
        setattr(instance, field, geo.get(field, default))


def enrich_instance_geo(instance: Any, ip: Optional[str]) -> bool:
    """Backfill missing coordinates on a saved record. Returns True if updated."""
    if not ip or is_private_ip(ip):
        return False
    if instance.latitude is not None and instance.longitude is not None:
        return False

    geo = lookup_ip(ip)
    if geo.get('latitude') is None or geo.get('longitude') is None:
        return False

    for field in GEO_FIELDS:
        default = '' if field in ('country', 'city', 'isp', 'asn') else None
        setattr(instance, field, geo.get(field, default))
    instance.save(update_fields=list(GEO_FIELDS))
    return True


def enrich_missing_geolocation(limit: int = 40) -> int:
    """Backfill geo for recent records missing coordinates."""
    from ..models import AccessLog, BotSignal

    updated = 0

    for log in AccessLog.objects.filter(
        latitude__isnull=True,
    ).exclude(ip_address__isnull=True).order_by('-timestamp')[:limit]:
        if enrich_instance_geo(log, log.ip_address):
            updated += 1

    for signal in BotSignal.objects.filter(
        latitude__isnull=True,
    ).exclude(source_ip__isnull=True).order_by('-timestamp')[:limit]:
        if enrich_instance_geo(signal, signal.source_ip):
            updated += 1

    return updated
