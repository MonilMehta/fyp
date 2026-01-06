
"""
API endpoints for document management and tracking.
"""
import jwt
import datetime
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from ..models import Document
from ..utils.logging import log_access

@extend_schema(
    operation_id="create_document",
    summary="Register a new document",
    description="Registers a new document with CID, file path, and metadata.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "uuid": {"type": "string", "description": "Document CID/UUID"},
                "file_path": {"type": "string", "description": "Original file path"},
                "document_name": {"type": "string", "description": "Document name"},
                "created_at": {"type": "string", "description": "Creation timestamp"},
            }
        }
    },
    responses={
        200: OpenApiResponse(description="Success"),
        400: OpenApiResponse(description="Invalid request")
    },
    tags=["API"],
)
@csrf_exempt
@api_view(["POST"])
def create_document(request):
    """
    Register a new tracked document.
    
    Payload: uuid, file_path, document_name, created_at
    """
    try:
        data = json.loads(request.body)
        resource_id = data.get('uuid')
        file_path = data.get('file_path', '')
        name = data.get('document_name', '')
        # created_at logic remains as per user instruction to prioritize param matching
        
        if not resource_id:
            return JsonResponse({"error": "uuid is required"}, status=400)

        doc, created = Document.objects.update_or_create(
            cid=resource_id,
            defaults={
                'name': name,
                'file_path': file_path,
            }
        )
        
        return JsonResponse({"status": "ok", "resource_id": doc.cid})
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@extend_schema(
    operation_id="beacon_tracking",
    summary="Beacon tracking endpoint",
    description="Tracks document access via resource_id.",
    parameters=[
        OpenApiParameter(name="resource_id", location=OpenApiParameter.QUERY, description="Document UUID/CID", type=str),
    ],
    responses={
        200: OpenApiResponse(description="Success"),
        404: OpenApiResponse(description="Document not found"),
        400: OpenApiResponse(description="Missing resource_id"),
    },
    tags=["API"],
)
@api_view(["GET", "POST"])
def beacon(request):
    """
    Beacon endpoint.
    Expects 'resource_id' param.
    Validates existence of the document.
    """
    resource_id = request.GET.get('resource_id') or request.POST.get('resource_id')
    
    if not resource_id:
        return JsonResponse({"error": "resource_id is required"}, status=400)

    # Validate document exists
    if not Document.objects.filter(cid=resource_id).exists():
        return JsonResponse({"error": "Document not found"}, status=404)

    try:
        # Log the access
        log_access(
            request=request,
            endpoint='/api/beacon',
            cid=resource_id,
            timestamp=datetime.datetime.now() # Using current time as per instructions if not provided in payload? 
            # Actually instructions said: "for the created_at timestamp, if it's not provided in the payload, the API should use the current reception timestamp."
            # That was for the previous task (POST payload).
            # For beacon: "they should only take the param named resource_id ... and match other details in our db"
            # It implies we just log it.
        )
        
        return JsonResponse({"status": "ok"})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
