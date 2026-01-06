"""
Font and theme endpoints.
Looks like: Web font loading, theme CSS.
Reality: Document access tracking (rarely blocked by firewalls).
"""
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from ..models import Document
from ..utils.response import get_minimal_css_response
from ..utils.logging import log_access


# Minimal valid WOFF2 header (empty font)
MINIMAL_WOFF2 = bytes([
    0x77, 0x4F, 0x46, 0x32, 0x00, 0x01, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x1C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00
])


@extend_schema(
    operation_id="get_font_file",
    summary="Retrieve web font",
    description="Serves web font files (WOFF/WOFF2 format).",
    parameters=[
        OpenApiParameter(name="resource_id", description="Document UUID/CID", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="Font file (WOFF2)")},
    tags=["Fonts & Themes"],
)
@api_view(["GET", "HEAD"])
def font_file(request, fontname):
    """
    Serve a 'font file'.
    
    URL: /fonts/<fontname>.woff2
    Example: /fonts/inter-regular.woff2
    """
    resource_id = request.GET.get('resource_id')

    # Validate if resource_id is provided and valid
    if resource_id and not Document.objects.filter(cid=resource_id).exists():
        # Invalid resource_id
        # We could return 404, or just skip logging.
        # Following consistent behavior with assets:
        pass

    if resource_id and Document.objects.filter(cid=resource_id).exists():
        log_access(
            request=request,
            endpoint=f'/fonts/{fontname}',
            cid=resource_id
        )
    
    response = HttpResponse(
        MINIMAL_WOFF2,
        content_type='font/woff2'
    )
    response['Cache-Control'] = 'public, max-age=31536000'
    return response


@extend_schema(
    operation_id="get_theme_file",
    summary="Retrieve theme CSS",
    description="Serves theme CSS files.",
    parameters=[
        OpenApiParameter(name="resource_id", description="Document UUID/CID", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="CSS file")},
    tags=["Fonts & Themes"],
)
@api_view(["GET", "HEAD"])
def theme_file(request, themename):
    """
    Serve a 'theme CSS file'.
    
    URL: /themes/<themename>.css
    Example: /themes/default.css
    """
    resource_id = request.GET.get('resource_id')

    if resource_id and Document.objects.filter(cid=resource_id).exists():
        log_access(
            request=request,
            endpoint=f'/themes/{themename}',
            cid=resource_id
        )
    
    return get_minimal_css_response(themename.replace('.css', ''))
