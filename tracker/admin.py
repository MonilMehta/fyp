from django.contrib import admin
from .models import Document, AccessLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('cid', 'name', 'created_at', 'access_count')
    search_fields = ('cid', 'name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    def access_count(self, obj):
        return obj.access_logs.count()
    access_count.short_description = 'Render Events'


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = (
        'short_endpoint', 'cid', 'ip_address', 'country',
        'client_app', 'timestamp', 'is_first_access'
    )
    list_filter = (
        'is_first_access', 'is_proxy', 'is_tor',
        'country', 'client_app', 'timestamp'
    )
    search_fields = ('cid', 'ip_address', 'user_agent', 'endpoint')
    readonly_fields = (
        'document', 'cid', 'ip_address', 'asn', 'isp', 'country', 'city',
        'is_proxy', 'is_tor', 'user_agent', 'accept_headers', 'accept_language',
        'os_name', 'os_version', 'browser_name', 'browser_version',
        'client_app', 'client_build', 'endpoint', 'method', 'query_params',
        'request_body', 'timestamp', 'clock_skew', 'is_first_access', 'session_id'
    )
    date_hierarchy = 'timestamp'

    def short_endpoint(self, obj):
        return obj.endpoint[:50] + '...' if len(obj.endpoint) > 50 else obj.endpoint
    short_endpoint.short_description = 'Asset Path'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
