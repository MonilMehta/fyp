"""
Dashboard views for the tracking system.
Uses stealth terminology: "Document Assets", "Render Events", "Client Signals".
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta

from ..models import Document, AccessLog


def index(request):
    """Main dashboard with overview statistics."""
    # Get time ranges
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    # Overall stats
    total_documents = Document.objects.count()
    total_events = AccessLog.objects.count()
    events_24h = AccessLog.objects.filter(timestamp__gte=last_24h).count()
    events_7d = AccessLog.objects.filter(timestamp__gte=last_7d).count()

    # Unique IPs
    unique_ips = AccessLog.objects.values('ip_address').distinct().count()
    unique_ips_24h = AccessLog.objects.filter(
        timestamp__gte=last_24h
    ).values('ip_address').distinct().count()

    # Top accessed documents
    top_documents = Document.objects.annotate(
        event_count=Count('access_logs')
    ).order_by('-event_count')[:10]

    # Recent events
    recent_events = AccessLog.objects.select_related('document').order_by('-timestamp')[:20]

    # Events by endpoint
    events_by_endpoint = AccessLog.objects.values('endpoint').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Events by country
    events_by_country = AccessLog.objects.exclude(
        country=''
    ).values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Events by client app
    events_by_client = AccessLog.objects.exclude(
        client_app=''
    ).values('client_app').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Hourly activity (last 24h)
    hourly_activity = AccessLog.objects.filter(
        timestamp__gte=last_24h
    ).annotate(
        hour=TruncHour('timestamp')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')

    # Advanced Stats
    # 1. Device Category (Desktop vs Mobile)
    mobile_keywords = ['Android', 'iPhone', 'iPad', 'Mobile']
    device_stats = {
        'mobile': 0,
        'desktop': 0,
        'office': 0
    }
    
    # Analyze detailed user agents for categories
    all_uas = AccessLog.objects.values('user_agent', 'client_app')
    for ua in all_uas:
        ua_str = ua['user_agent']
        client = ua['client_app']
        
        if 'Office' in client or 'Word' in client or 'Excel' in client:
            device_stats['office'] += 1
        elif any(k in ua_str for k in mobile_keywords):
            device_stats['mobile'] += 1
        else:
            device_stats['desktop'] += 1

    # 2. Top ISPs (Corporate Identification)
    top_isps = AccessLog.objects.exclude(isp='').values('isp').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'total_documents': total_documents,
        'total_events': total_events,
        'events_24h': events_24h,
        'events_7d': events_7d,
        'unique_ips': unique_ips,
        'unique_ips_24h': unique_ips_24h,
        'top_documents': top_documents,
        'recent_events': recent_events,
        'events_by_endpoint': events_by_endpoint,
        'events_by_country': events_by_country,
        'events_by_client': events_by_client,
        'hourly_activity': list(hourly_activity),
        'device_stats': device_stats,
        'top_isps': top_isps,
    }
    return render(request, 'dashboard/index.html', context)


def events_list(request):
    """List all render events with filtering."""
    # Get filter parameters
    cid = request.GET.get('cid', '')
    ip = request.GET.get('ip', '')
    endpoint = request.GET.get('endpoint', '')
    country = request.GET.get('country', '')
    client = request.GET.get('client', '')
    first_access = request.GET.get('first_access', '')

    # Build queryset
    events = AccessLog.objects.select_related('document').order_by('-timestamp')

    if cid:
        events = events.filter(cid__icontains=cid)
    if ip:
        events = events.filter(ip_address__icontains=ip)
    if endpoint:
        events = events.filter(endpoint__icontains=endpoint)
    if country:
        events = events.filter(country__icontains=country)
    if client:
        events = events.filter(client_app__icontains=client)
    if first_access == 'true':
        events = events.filter(is_first_access=True)

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 50
    total = events.count()
    events = events[(page-1)*per_page:page*per_page]

    context = {
        'events': events,
        'filters': {
            'cid': cid,
            'ip': ip,
            'endpoint': endpoint,
            'country': country,
            'client': client,
            'first_access': first_access,
        },
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
        }
    }
    return render(request, 'dashboard/events.html', context)


def event_detail(request, event_id):
    """View full details of a single event."""
    event = get_object_or_404(AccessLog, id=event_id)
    
    # Get related events (same CID or IP)
    related_by_cid = []
    related_by_ip = []
    
    if event.cid:
        related_by_cid = AccessLog.objects.filter(
            cid=event.cid
        ).exclude(id=event.id).order_by('-timestamp')[:10]
    
    if event.ip_address:
        related_by_ip = AccessLog.objects.filter(
            ip_address=event.ip_address
        ).exclude(id=event.id).order_by('-timestamp')[:10]

    context = {
        'event': event,
        'related_by_cid': related_by_cid,
        'related_by_ip': related_by_ip,
    }
    return render(request, 'dashboard/event_detail.html', context)


def documents_list(request):
    """List all tracked documents."""
    documents = Document.objects.annotate(
        event_count=Count('access_logs'),
        first_access=Min('access_logs__timestamp'),
        last_access=Max('access_logs__timestamp'),
    ).order_by('-event_count')

    context = {
        'documents': documents,
    }
    return render(request, 'dashboard/documents.html', context)


def document_detail(request, doc_id):
    """View full details of a document."""
    document = get_object_or_404(Document, id=doc_id)
    
    events = document.access_logs.order_by('-timestamp')[:50]
    
    # Stats for this document
    unique_ips = document.access_logs.values('ip_address').distinct().count()
    unique_countries = document.access_logs.exclude(
        country=''
    ).values('country').distinct().count()

    context = {
        'document': document,
        'events': events,
        'unique_ips': unique_ips,
        'unique_countries': unique_countries,
    }
    return render(request, 'dashboard/document_detail.html', context)


# API endpoints for dashboard charts
def api_hourly_activity(request):
    """Get hourly activity for charts."""
    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    
    data = AccessLog.objects.filter(
        timestamp__gte=since
    ).annotate(
        hour=TruncHour('timestamp')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    return JsonResponse({
        'labels': [d['hour'].strftime('%H:%M') for d in data],
        'values': [d['count'] for d in data],
    })


def api_events_by_endpoint(request):
    """Get events grouped by endpoint."""
    data = AccessLog.objects.values('endpoint').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return JsonResponse({
        'labels': [d['endpoint'][:30] for d in data],
        'values': [d['count'] for d in data],
    })


# Import Min/Max for aggregation
from django.db.models.functions import TruncHour
from django.db.models import Min, Max
