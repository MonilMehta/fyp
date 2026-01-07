
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
    summary="Register new document(s)",
    description="Registers one or more documents with CID, file path, and metadata.",
    request={
        "application/json": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "uuid": {"type": "string", "description": "Document CID/UUID"},
                        "file_path": {"type": "string", "description": "Original file path"},
                        "document_name": {"type": "string", "description": "Document name"},
                        "created_at": {"type": "string", "description": "Creation timestamp"},
                    }
                },
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uuid": {"type": "string", "description": "Document CID/UUID"},
                            "file_path": {"type": "string", "description": "Original file path"},
                            "document_name": {"type": "string", "description": "Document name"},
                            "created_at": {"type": "string", "description": "Creation timestamp"},
                        }
                    }
                }
            ]
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
    Register new tracked document(s).
    
    Payload: uuid, file_path, document_name, created_at (as object or list of objects)
    """
    try:
        data = json.loads(request.body)
        
        if isinstance(data, list):
            items = data
        else:
            items = [data]
            
        processed_ids = []
        for item in items:
            resource_id = item.get('uuid')
            file_path = item.get('file_path', '')
            name = item.get('document_name', '')
            
            if not resource_id:
                continue

            doc, created = Document.objects.update_or_create(
                cid=resource_id,
                defaults={
                    'name': name,
                    'file_path': file_path,
                }
            )
            processed_ids.append(doc.cid)
        
        if not processed_ids and items:
            return JsonResponse({"error": "uuid is required for at least one item"}, status=400)

        # Return single id for backward compatibility if only one item was sent as object
        if not isinstance(data, list) and len(processed_ids) == 1:
            return JsonResponse({"status": "ok", "resource_id": processed_ids[0]})
            
        return JsonResponse({"status": "ok", "resource_ids": processed_ids})
        
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
