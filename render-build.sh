#!/bin/bash
# Run migrations
python manage.py migrate --noinput
# Collect static files
python manage.py collectstatic --noinput
echo "Database migrations and static files collected successfully"
