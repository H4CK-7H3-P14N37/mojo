#!/bin/bash
set -e

# Run database migrations
python manage.py migrate --noinput

# Create default superuser if not exists
echo "from django.contrib.auth import get_user_model; User = get_user_model(); x = not User.objects.filter(username='root').exists(); User.objects.create_superuser('root','root@redteam-test.com','redteamroxs') if x else None" | python manage.py shell

# Execute Gunicorn
exec gunicorn mojo.wsgi:application --bind 0.0.0.0:8000 --workers 3
