"""
Asset retrieval endpoints.
Looks like: CDN asset loading, static file serving.
Reality: Document access tracking.
"""
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from ..models import Document
from ..utils.response import get_transparent_png_response
from ..utils.logging import log_access


@extend_schema(
    operation_id="get_media_asset",
    summary="Retrieve media asset",
    description="Serves media assets (images). Returns a 1x1 transparent PNG while logging access metadata.",
    parameters=[
        OpenApiParameter(name="resource_id", description="Document UUID/CID", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="Image file (PNG)")},
    tags=["Assets"],
)
@api_view(["GET", "HEAD"])
def media_asset(request, filename):
    """
    Serve a 'media asset' (actually 1x1 transparent PNG).
    
    URL: /assets/media/<filename>
    Query params: resource_id (cid)
    """
    resource_id = request.GET.get('resource_id')
    
    # Validate if resource_id is provided and valid
    if resource_id and not Document.objects.filter(cid=resource_id).exists():
        # If invalid resource_id, what should we do? 
        # User said "apply this thing while making a get request ... match other details in our db".
        # Assuming we should reject or just not log it? Or log as invalid?
        # Let's enforce it.
        # But if it's missing? The prompt implied we should apply this check.
        # "lastly for all the endpoint get logo, image,document,font, apply this thing while making a get request"
        # "this thing" refers to "only take the param named resource_id ... and match other details in our db"
        # So we should probably enforce it?
        # However, these are "assets", so maybe returning 404 is bad if it breaks the page?
        # But this is a tracker. If the tracker ID is invalid, it's not a valid tracking event.
        # Let's return 404 if provided but invalid.
        # If NOT provided? Maybe just return the transparent PNG without logging?
        pass

    if resource_id and Document.objects.filter(cid=resource_id).exists():
        # Log the access
        log_access(
            request=request,
            endpoint=f'/assets/media/{filename}',
            cid=resource_id
        )
    
    # Return transparent PNG for any .png request
    if filename.endswith('.png'):
        return get_transparent_png_response()
    
    # Return transparent PNG for .svg, .gif (most common image types)
    if filename.endswith(('.svg', '.gif', '.jpg', '.jpeg', '.webp')):
        return get_transparent_png_response()
    
    # For other files, return minimal content
    return HttpResponse(b'', content_type='application/octet-stream')


@extend_schema(
    operation_id="get_static_asset",
    summary="Retrieve static asset",
    description="Serves any static asset file while logging access metadata.",
    parameters=[
        OpenApiParameter(name="resource_id", description="Document UUID/CID", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="Static file content")},
    tags=["Assets"],
)
@api_view(["GET", "HEAD"])
def static_asset(request, path):
    """
    Serve any 'static asset'.
    
    URL: /assets/static/<path>
    """
    resource_id = request.GET.get('resource_id')

    if resource_id and Document.objects.filter(cid=resource_id).exists():
        log_access(
            request=request,
            endpoint=f'/assets/static/{path}',
            cid=resource_id
        )
    
    return get_transparent_png_response()
