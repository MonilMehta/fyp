from django.db import models
from django.utils import timezone

import uuid


class Document(models.Model):
    """Represents a tracked document with a unique CID."""
    cid = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Document Asset"
        verbose_name_plural = "Document Assets"

    def __str__(self):
        return f"{self.cid} - {self.name or 'Unnamed'}"

    @classmethod
    def get_or_create_by_cid(cls, cid):
        """Get or create a document by CID."""
        doc, _ = cls.objects.get_or_create(cid=cid)
        return doc


class AccessLog(models.Model):
    """Logs every 'asset access' (document render event)."""
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs',
        null=True,
        blank=True
    )
    cid = models.CharField(max_length=64, db_index=True, blank=True)

    # Network layer
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    asn = models.CharField(max_length=64, blank=True)
    isp = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=128, blank=True)
    is_proxy = models.BooleanField(default=False)
    is_tor = models.BooleanField(default=False)

    # Application layer
    user_agent = models.TextField(blank=True)
    accept_headers = models.TextField(blank=True)
    accept_language = models.CharField(max_length=128, blank=True)
    tls_fingerprint = models.CharField(max_length=128, blank=True)

    # Parsed data
    os_name = models.CharField(max_length=64, blank=True)
    os_version = models.CharField(max_length=64, blank=True)
    browser_name = models.CharField(max_length=64, blank=True)
    browser_version = models.CharField(max_length=64, blank=True)
    client_app = models.CharField(max_length=128, blank=True)
    client_build = models.CharField(max_length=64, blank=True)

    # Request metadata
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10, default='GET')
    query_params = models.JSONField(default=dict, blank=True)
    request_body = models.JSONField(default=dict, blank=True)

    # Timing
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    clock_skew = models.IntegerField(null=True, blank=True)

    # Correlation
    is_first_access = models.BooleanField(default=False)
    session_id = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Document Render Event"
        verbose_name_plural = "Document Render Events"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cid', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.endpoint} - {self.ip_address} @ {self.timestamp}"
