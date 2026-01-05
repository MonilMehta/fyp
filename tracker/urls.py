"""
URL configuration for tracker app.
All routes designed to look like normal SaaS traffic.
"""
from django.urls import path, re_path

from django.urls import path, re_path

from .views import assets, config, telemetry, fonts, health, dashboard


urlpatterns = [
    # Dashboard endpoints
    path('dashboard/', dashboard.index, name='dashboard_index'),
    path('dashboard/events/', dashboard.events_list, name='dashboard_events'),
    path('dashboard/events/<int:event_id>/', dashboard.event_detail, name='dashboard_event_detail'),
    path('dashboard/documents/', dashboard.documents_list, name='dashboard_documents'),
    path('dashboard/documents/<int:doc_id>/', dashboard.document_detail, name='dashboard_document_detail'),
    path('dashboard/api/hourly/', dashboard.api_hourly_activity, name='api_hourly_activity'),
    path('dashboard/api/endpoints/', dashboard.api_events_by_endpoint, name='api_events_by_endpoint'),

    # Asset retrieval endpoints
    re_path(r'^assets/media/(?P<filename>.+)$', assets.media_asset, name='media_asset'),
    re_path(r'^assets/static/(?P<path>.+)$', assets.static_asset, name='static_asset'),
    
    # Configuration endpoints
    path('config/runtime.json', config.runtime_config, name='runtime_config'),
    path('config/ui-flags.json', config.ui_flags, name='ui_flags'),
    path('config/doc-settings.json', config.doc_settings, name='doc_settings'),
    
    # Telemetry endpoints
    path('telemetry/metrics', telemetry.metrics, name='telemetry_metrics'),
    path('telemetry/client', telemetry.client_info, name='telemetry_client'),
    path('telemetry/events', telemetry.events, name='telemetry_events'),
    
    # Font and theme endpoints
    re_path(r'^fonts/(?P<fontname>.+\.woff2?)$', fonts.font_file, name='font_file'),
    re_path(r'^themes/(?P<themename>.+\.css)$', fonts.theme_file, name='theme_file'),
    
    # Health and prefetch endpoints
    path('health/ping', health.ping, name='health_ping'),
    path('status/ready', health.ready, name='status_ready'),
    path('prefetch/init', health.prefetch_init, name='prefetch_init'),
]
