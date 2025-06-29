# FLX Web - Enterprise Web Dashboard

**Status**: ✅ Production Ready (Django Implementation)  
**Based on**: Real implementation from `flx-meltano-enterprise/src/flx_web/`

## Overview

FLX Web provides a comprehensive Django-based web dashboard for the FLX platform. This is a full-stack Django application with server-side rendering, NOT a React/Vue SPA as might be expected. The implementation is complete with 0 NotImplementedError.

## Real Implementation Status

| Component           | Implementation   | Status      | Details                             |
| ------------------- | ---------------- | ----------- | ----------------------------------- |
| **Backend**         | Django 5.x       | ✅ Complete | Full Django with 5 apps             |
| **Frontend**        | Django Templates | ✅ Complete | Bootstrap 5 + Server-side rendering |
| **Database**        | Django ORM       | ✅ Complete | Models with migrations              |
| **API Integration** | gRPC             | ✅ Complete | Connects to FLX services            |
| **Admin Interface** | Django Admin     | ✅ Complete | Full CRUD interfaces                |

**Total**: 3,930+ lines of Django code with 0 NotImplementedError

## Architecture Reality

This is a **Django Monolith**, not a decoupled frontend/backend:

```
flx_web/
├── Django Project (flx_web/)
│   ├── settings/          # Environment-based config
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── Django Apps (apps/)
│   ├── dashboard/        # Real-time monitoring
│   ├── projects/         # Project management
│   ├── pipelines/        # Pipeline management
│   ├── monitoring/       # System monitoring
│   └── users/           # User management
└── Templates & Static/
    ├── templates/        # Django templates
    └── static/          # CSS, JS, images
```

## Django Apps

### 1. Dashboard App (351 lines)

- Real-time system statistics
- Pipeline execution monitoring
- Health status display
- gRPC integration for live data

### 2. Projects App (1,116 lines)

- Project CRUD operations
- Template management
- Deployment tracking
- Full admin interface

### 3. Pipelines App (653 lines)

- Pipeline configuration
- Execution history
- Schedule management
- Status monitoring

### 4. Monitoring App (850 lines)

- System metrics display
- Alert management
- Performance tracking
- Resource utilization

### 5. Users App (540 lines)

- Extended user model
- Role management
- Authentication views
- Profile management

## Features

### Core Functionality

- **Server-Side Rendering**: Traditional Django templates
- **Bootstrap 5 UI**: Responsive design
- **gRPC Integration**: Connects to backend services
- **Real-Time Updates**: Via page refresh (no WebSockets)
- **Admin Interface**: Full Django admin customization

### Enterprise Features

- **Multi-Environment**: Dev/staging/production configs
- **WhiteNoise**: Static file serving
- **Security Headers**: CSP, HSTS, etc.
- **Session Management**: Database-backed sessions
- **CSRF Protection**: Django middleware

## Quick Start

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Run production server
gunicorn flx_web.wsgi:application
```

## Configuration

```python
# Required environment variables
DJANGO_SECRET_KEY=your-secret-key-50-chars
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@localhost/flx_web

# gRPC Backend
GRPC_HOST=localhost
GRPC_PORT=50051

# Static files
STATIC_ROOT=/var/www/flx_web/static
MEDIA_ROOT=/var/www/flx_web/media

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## UI Technology Stack

- **Django Templates**: Server-side rendering
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icon library
- **jQuery**: Limited JavaScript interactions
- **No SPA Framework**: No React/Vue/Angular

## URL Structure

```
/                    # Dashboard home
/admin/              # Django admin
/projects/           # Project listing
/projects/<id>/      # Project detail
/pipelines/          # Pipeline listing
/pipelines/<id>/     # Pipeline detail
/monitoring/         # System monitoring
/users/profile/      # User profile
/login/              # Authentication
/logout/             # Logout
```

## Database Models

```python
# Key models implemented
class PipelineWeb(models.Model):
    pipeline_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    pipeline_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User)

class Deployment(models.Model):
    project = models.ForeignKey(Project)
    environment = models.CharField(max_length=50)
    deployed_at = models.DateTimeField()
```

## Production Deployment

### Static Files

```bash
# WhiteNoise configuration
python manage.py collectstatic --noinput
# Files served from STATIC_ROOT
```

### Database

```bash
# PostgreSQL recommended
python manage.py migrate --noinput
```

### Web Server

```nginx
# Nginx configuration
location / {
    proxy_pass http://unix:/run/gunicorn.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /static/ {
    alias /var/www/flx_web/static/;
}
```

## Testing

```bash
# Django tests
python manage.py test

# Coverage report
coverage run --source='.' manage.py test
coverage report

# Integration tests
python manage.py test apps.dashboard.tests.integration
```

## Important Note on Frontend

The `frontend/` directory exists but is **EMPTY**. This Django application does NOT use:

- ❌ React
- ❌ Vue
- ❌ Angular
- ❌ Any SPA framework

It uses traditional Django server-side rendering with templates.

## Security

- Django's built-in security middleware
- CSRF protection on all forms
- SQL injection prevention via ORM
- XSS protection in templates
- Secure session cookies
- HTTPS enforcement in production

## License

Part of the FLX Platform - Enterprise License
