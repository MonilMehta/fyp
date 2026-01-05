"""
Health and prefetch endpoints.
Looks like: Load balancer checks, SPA warmups.
Reality: Background noise tracking.
"""
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from ..utils.logging import log_access


@extend_schema(
    operation_id="health_ping",
    summary="Health check ping",
    description="Simple health check endpoint returning 'ok'.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={200: OpenApiResponse(description="Plain text 'ok'")},
    tags=["Health"],
)
@api_view(["GET", "HEAD"])
def ping(request):
    """
    Health check ping.
    
    URL: /health/ping
    """
    log_access(
        request=request,
        endpoint='/health/ping',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return HttpResponse("ok", content_type='text/plain')


@extend_schema(
    operation_id="status_ready",
    summary="Readiness check",
    description="Returns service readiness status.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            description="Readiness status",
            examples=[OpenApiExample("Ready", value={"status": "ready", "healthy": True})]
        )
    },
    tags=["Health"],
)
@api_view(["GET", "HEAD"])
def ready(request):
    """
    Readiness check.
    
    URL: /status/ready
    """
    log_access(
        request=request,
        endpoint='/status/ready',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return JsonResponse({"status": "ready", "healthy": True})


@extend_schema(
    operation_id="prefetch_init",
    summary="Prefetch initialization",
    description="Returns prefetch configuration for client caching.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            description="Prefetch config",
            examples=[OpenApiExample("Config", value={"preload": [], "cache": True, "ttl": 3600})]
        )
    },
    tags=["Health"],
)
@api_view(["GET", "HEAD"])
def prefetch_init(request):
    """
    Prefetch initialization.
    
    URL: /prefetch/init
    """
    log_access(
        request=request,
        endpoint='/prefetch/init',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return JsonResponse({
        "preload": [],
        "cache": True,
        "ttl": 3600
    })
