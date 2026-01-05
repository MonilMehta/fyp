"""
Configuration fetch endpoints.
Looks like: Feature flags, UI config, document settings.
Reality: Document access tracking with static responses.
"""
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from ..utils.response import (
    get_json_response,
    CONFIG_RUNTIME,
    CONFIG_UI_FLAGS,
    CONFIG_DOC_SETTINGS,
)
from ..utils.logging import log_access


@extend_schema(
    operation_id="get_runtime_config",
    summary="Get runtime configuration",
    description="Returns runtime configuration settings for the application.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            description="Runtime configuration",
            examples=[
                OpenApiExample(
                    "Default response",
                    value={"theme": "light", "density": "comfortable", "version": "2.4.1"}
                )
            ]
        )
    },
    tags=["Configuration"],
)
@api_view(["GET", "HEAD"])
def runtime_config(request):
    """
    Return runtime configuration.
    
    URL: /config/runtime.json
    """
    log_access(
        request=request,
        endpoint='/config/runtime.json',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return get_json_response(CONFIG_RUNTIME)


@extend_schema(
    operation_id="get_ui_flags",
    summary="Get UI feature flags",
    description="Returns UI feature flag settings.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            description="UI feature flags",
            examples=[
                OpenApiExample(
                    "Default response",
                    value={"features": {"tables": True, "charts": False, "comments": True}, "experimental": {}}
                )
            ]
        )
    },
    tags=["Configuration"],
)
@api_view(["GET", "HEAD"])
def ui_flags(request):
    """
    Return UI feature flags.
    
    URL: /config/ui-flags.json
    """
    log_access(
        request=request,
        endpoint='/config/ui-flags.json',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return get_json_response(CONFIG_UI_FLAGS)


@extend_schema(
    operation_id="get_doc_settings",
    summary="Get document settings",
    description="Returns document rendering settings.",
    parameters=[
        OpenApiParameter(name="cid", description="Client ID", required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            description="Document settings",
            examples=[
                OpenApiExample(
                    "Default response",
                    value={"page_size": "A4", "margins": "normal", "orientation": "portrait", "render_mode": "standard"}
                )
            ]
        )
    },
    tags=["Configuration"],
)
@api_view(["GET", "HEAD"])
def doc_settings(request):
    """
    Return document settings.
    
    URL: /config/doc-settings.json
    """
    log_access(
        request=request,
        endpoint='/config/doc-settings.json',
        cid=request.GET.get('cid', request.GET.get('c'))
    )
    
    return get_json_response(CONFIG_DOC_SETTINGS)
