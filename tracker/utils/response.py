"""
Response utilities for generating stealth content.
"""
import base64
from django.http import HttpResponse


# 1x1 transparent PNG (smallest valid PNG)
TRANSPARENT_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

TRANSPARENT_PNG_BYTES = base64.b64decode(TRANSPARENT_PNG_BASE64)

# Minimal valid WOFF2 (empty font placeholder)
MINIMAL_WOFF2_BASE64 = (
    "d09GMgABAAAAAADcAA4AAAAAATQAAADNAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP0ZGVE0cGh4GYACCahEICgAL"
    "EAABNgIkAwgEBgWDJAcgGwHwBhxk7xsv5aeSF3j+v0/n5P3/n5lZd3eZmZm7u8zM"
)

# Standard config responses
CONFIG_RUNTIME = {
    "theme": "light",
    "density": "comfortable",
    "version": "2.4.1",
}

CONFIG_UI_FLAGS = {
    "features": {
        "tables": True,
        "charts": False,
        "comments": True,
        "track_changes": False,
    },
    "experimental": {},
}

CONFIG_DOC_SETTINGS = {
    "page_size": "A4",
    "margins": "normal",
    "orientation": "portrait",
    "render_mode": "standard",
}


def get_transparent_png_response() -> HttpResponse:
    """Return a 1x1 transparent PNG response."""
    response = HttpResponse(
        TRANSPARENT_PNG_BYTES,
        content_type='image/png'
    )
    response['Cache-Control'] = 'public, max-age=31536000'
    response['Content-Length'] = len(TRANSPARENT_PNG_BYTES)
    return response


def get_minimal_css_response(theme_name: str = 'default') -> HttpResponse:
    """Return minimal valid CSS."""
    css_content = f"/* {theme_name} theme */\n:root {{ --theme: {theme_name}; }}\n"
    response = HttpResponse(css_content, content_type='text/css')
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def get_json_response(data: dict, cache_seconds: int = 300) -> HttpResponse:
    """Return a JSON response with proper headers."""
    import json
    response = HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )
    response['Cache-Control'] = f'public, max-age={cache_seconds}'
    return response
