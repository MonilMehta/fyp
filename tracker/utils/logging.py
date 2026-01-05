"""
Logging service for tracking document access.
Uses stealth terminology throughout.
"""
from typing import Optional
from ..models import Document, AccessLog
from .fingerprint import extract_request_metadata, extract_query_params


def log_access(
    request,
    endpoint: str,
    cid: Optional[str] = None,
    request_body: Optional[dict] = None
) -> AccessLog:
    """
    Log a document render event.
    
    Args:
        request: Django HttpRequest object
        endpoint: The endpoint path being accessed
        cid: Optional CID extracted from query params
        request_body: Optional request body for POST requests
    
    Returns:
        AccessLog instance
    """
    # Extract metadata
    metadata = extract_request_metadata(request)
    query_params = extract_query_params(request)
    
    # Get CID from query params if not provided
    if not cid:
        cid = query_params.get('cid', query_params.get('c', ''))
    
    # Link to document if CID exists
    document = None
    is_first_access = False
    if cid:
        document = Document.get_or_create_by_cid(cid)
        is_first_access = not document.access_logs.exists()
    
    # Create access log
    access_log = AccessLog.objects.create(
        document=document,
        cid=cid,
        endpoint=endpoint,
        method=request.method,
        query_params=query_params,
        request_body=request_body or {},
        is_first_access=is_first_access,
        **metadata
    )
    
    return access_log


def log_telemetry(request, endpoint: str, payload: dict) -> AccessLog:
    """Log telemetry/client signal events."""
    # Extract client info from payload
    client_app = payload.get('client', '')
    client_build = payload.get('build', '')
    
    access_log = log_access(
        request=request,
        endpoint=endpoint,
        request_body=payload
    )
    
    # Update with payload-specific data
    if client_app and not access_log.client_app:
        access_log.client_app = client_app
    if client_build and not access_log.client_build:
        access_log.client_build = client_build
    access_log.save()
    
    return access_log
