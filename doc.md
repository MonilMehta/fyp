# Document Asset Tracker API

A stealth document tracking system designed to monitor document access events by masquerading as a SaaS asset server.

## Overview

This API provides endpoints that appear to be standard SaaS infrastructure (asset delivery, configuration, telemetry) but actually track and log document access events with full client fingerprinting.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Production Deployment

```bash
# Set environment variables
export DJANGO_SECRET_KEY="your-secure-secret-key"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="yourdomain.com"
export CSRF_TRUSTED_ORIGINS="https://yourdomain.com"

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn fyp.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | insecure-key | Secret key for cryptographic signing |
| `DJANGO_DEBUG` | True | Enable debug mode (set to False in production) |
| `DJANGO_ALLOWED_HOSTS` | * | Comma-separated list of allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | localhost | Comma-separated list of trusted origins |

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

---

## Endpoints

### Assets

Endpoints that serve "media assets" (actually 1x1 transparent PNGs) while logging access.

#### GET `/assets/media/{filename}`

Serves media assets. Returns a 1x1 transparent PNG for any image request.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `filename` | path | Asset filename (e.g., `logo-light.png`) |
| `v` | query | Version string (for cache busting) |
| `cid` | query | Client/Cache ID (tracking identifier) |
| `r` | query | Region code |

**Example:**
```
GET /assets/media/logo-light.png?v=2.4.1&cid=7f3a9c&r=us
```

#### GET `/assets/static/{path}`

Serves any static asset file while logging access.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `path` | path | Asset path |
| `cid` | query | Client ID |

---

### Configuration

Endpoints that return static JSON configurations while logging access.

#### GET `/config/runtime.json`

Returns runtime configuration.

**Response:**
```json
{
  "theme": "light",
  "density": "comfortable",
  "version": "2.4.1"
}
```

#### GET `/config/ui-flags.json`

Returns UI feature flags.

**Response:**
```json
{
  "features": {
    "tables": true,
    "charts": false,
    "comments": true,
    "track_changes": false
  },
  "experimental": {}
}
```

#### GET `/config/doc-settings.json`

Returns document rendering settings.

**Response:**
```json
{
  "page_size": "A4",
  "margins": "normal",
  "orientation": "portrait",
  "render_mode": "standard"
}
```

---

### Telemetry

POST endpoints that accept client telemetry while logging access.

#### POST `/telemetry/metrics`

Accepts performance metrics.

**Request Body:**
```json
{
  "event": "document_render",
  "ts": 1735929123,
  "duration": 250
}
```

**Response:**
```json
{"status": "ok"}
```

#### POST `/telemetry/client`

Accepts client information.

**Request Body:**
```json
{
  "client": "office-word",
  "build": "16.0.17328",
  "platform": "Windows"
}
```

**Response:**
```json
{"status": "ok"}
```

#### POST `/telemetry/events`

Accepts event data.

**Request Body:**
```json
{
  "event": "document_open",
  "ts": 1735929123,
  "data": {"page": 1}
}
```

**Response:**
```json
{"status": "ok"}
```

---

### Fonts & Themes

Endpoints that serve font and theme files (rarely blocked by firewalls).

#### GET `/fonts/{fontname}.woff2`

Serves a web font file (minimal valid WOFF2).

**Example:**
```
GET /fonts/inter-regular.woff2?cid=abc123
```

#### GET `/themes/{themename}.css`

Serves a theme CSS file.

**Example:**
```
GET /themes/default.css?cid=abc123
```

---

### Health

Health check endpoints that blend into normal infrastructure traffic.

#### GET `/health/ping`

Simple health check.

**Response:** `ok` (text/plain)

#### GET `/status/ready`

Readiness check.

**Response:**
```json
{"status": "ready", "healthy": true}
```

#### GET `/prefetch/init`

Prefetch initialization.

**Response:**
```json
{
  "preload": [],
  "cache": true,
  "ttl": 3600
}
```

---

## Dashboard

Access the monitoring dashboard at `/dashboard/`

### Dashboard Pages

| URL | Description |
|-----|-------------|
| `/dashboard/` | Overview with stats, charts, and recent events |
| `/dashboard/events/` | List all access events with filtering |
| `/dashboard/events/{id}/` | Detailed view of a single event |
| `/dashboard/documents/` | List all tracked documents |
| `/dashboard/documents/{id}/` | Detailed view of a document |

### Dashboard API Endpoints

| URL | Description |
|-----|-------------|
| `/dashboard/api/hourly/?hours=24` | Hourly activity data for charts |
| `/dashboard/api/endpoints/` | Events grouped by endpoint |

---

## Data Captured

Each access event captures:

### Network Layer
- IP address
- ASN / ISP
- Geolocation (country, city)
- Proxy / TOR detection

### Application Layer
- User-Agent string
- Accept headers
- Accept-Language
- OS name and version
- Browser name and version
- Client application (Word, Excel, etc.)

### Request Metadata
- Endpoint accessed
- HTTP method
- Query parameters
- Request body (for POST)
- Timestamp

### Correlation
- Document CID
- First access flag
- Session tracking

---

## Embedding Tracking Links

Embed these URLs in documents to track access:

### In DOCX/HTML
```html
<img src="https://yourdomain.com/assets/media/logo.png?cid=UNIQUE_DOC_ID" width="1" height="1" />
```

### Remote Config Reference
```html
<link rel="stylesheet" href="https://yourdomain.com/themes/default.css?cid=UNIQUE_DOC_ID" />
```

### Font Loading
```css
@font-face {
  font-family: 'DocFont';
  src: url('https://yourdomain.com/fonts/inter.woff2?cid=UNIQUE_DOC_ID');
}
```

---

## Seeding Test Data

Generate sample data for testing:

```bash
python manage.py seed_data --events 100 --documents 10
```

---

## Admin Panel

Django admin is available at `/admin/` for direct database access.

