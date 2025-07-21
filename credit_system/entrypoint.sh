#!/bin/sh

# Wait for the database to be ready
/wait-for-it.sh db:5432 --timeout=60 --strict -- echo "Database is up"

# Run migrations
echo "Running Django migrations..."
python manage.py migrate

# Execute the given command (web server or celery worker)
exec "$@" 