"""
Telemetry endpoints.
Looks like: Performance metrics, usage analytics, error reporting.
Reality: Client signal capture with intelligence extraction.
"""
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from ..utils.logging import log_telemetry


@extend_schema(
    operation_id="post_telemetry_metrics",
    summary="Submit performance metrics",
    description="Accepts performance metrics data from clients.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "description": "Event type"},
                "ts": {"type": "integer", "description": "Timestamp"},
                "duration": {"type": "number", "description": "Duration in ms"},
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Success",
            examples=[OpenApiExample("Success", value={"status": "ok"})]
        )
    },
    tags=["Telemetry"],
)
@api_view(["POST"])
def metrics(request):
    """
    Accept performance metrics.
    
    URL: POST /telemetry/metrics
    """
    try:
        payload = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        payload = {}
    
    log_telemetry(
        request=request,
        endpoint='/telemetry/metrics',
        payload=payload
    )
    
    return JsonResponse({"status": "ok"})


@extend_schema(
    operation_id="post_telemetry_client",
    summary="Submit client information",
    description="Accepts client information and environment details.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "client": {"type": "string", "description": "Client application name"},
                "build": {"type": "string", "description": "Build version"},
                "platform": {"type": "string", "description": "Platform/OS"},
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Success",
            examples=[OpenApiExample("Success", value={"status": "ok"})]
        )
    },
    tags=["Telemetry"],
)
@api_view(["POST"])
def client_info(request):
    """
    Accept client information.
    
    URL: POST /telemetry/client
    """
    try:
        payload = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        payload = {}
    
    log_telemetry(
        request=request,
        endpoint='/telemetry/client',
        payload=payload
    )
    
    return JsonResponse({"status": "ok"})


@extend_schema(
    operation_id="post_telemetry_events",
    summary="Submit event data",
    description="Accepts event data for analytics.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "description": "Event name"},
                "ts": {"type": "integer", "description": "Timestamp"},
                "data": {"type": "object", "description": "Event data"},
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Success",
            examples=[OpenApiExample("Success", value={"status": "ok"})]
        )
    },
    tags=["Telemetry"],
)
@api_view(["POST"])
def events(request):
    """
    Accept event data.
    
    URL: POST /telemetry/events
    """
    try:
        payload = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        payload = {}
    
    log_telemetry(
        request=request,
        endpoint='/telemetry/events',
        payload=payload
    )
    
    return JsonResponse({"status": "ok"})
