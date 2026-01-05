"""
Asset retrieval endpoints.
Looks like: CDN asset loading, static file serving.
Reality: Document access tracking.
"""
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from ..utils.response import get_transparent_png_response
from ..utils.logging import log_access


@extend_schema(
    operation_id="get_media_asset",
    summary="Retrieve media asset",
    description="Serves media assets (images). Returns a 1x1 transparent PNG while logging access metadata.",
    parameters=[
        OpenApiParameter(name="filename", location=OpenApiParameter.PATH, description="Asset filename", type=str),
        OpenApiParameter(name="v", description="Asset version", required=False, type=str),
        OpenApiParameter(name="cid", description="Cache/Client ID", required=False, type=str),
        OpenApiParameter(name="r", description="Region code", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="Image file (PNG)")},
    tags=["Assets"],
)
@api_view(["GET", "HEAD"])
def media_asset(request, filename):
    """
    Serve a 'media asset' (actually 1x1 transparent PNG).
    
    URL: /assets/media/<filename>
    Query params: v (version), cid (cache id), r (region)
    
    Example: /assets/media/logo-light.png?v=2.4.1&cid=7f3a9c&r=us
    """
    # Log the access
    log_access(
        request=request,
        endpoint=f'/assets/media/{filename}',
        cid=request.GET.get('cid', request.GET.get('c'))
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
        OpenApiParameter(name="path", location=OpenApiParameter.PATH, description="Asset path", type=str),
        OpenApiParameter(name="cid", description="Cache/Client ID", required=False, type=str),
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
    log_access(
        request=request,
        endpoint=f'/assets/static/{path}',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return get_transparent_png_response()
