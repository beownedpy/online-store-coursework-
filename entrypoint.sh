#!/bin/sh

set -e


#Create Django project if config/settings.py is missing
if [ ! -f "config/settings.py" ]; then
  echo "No Django project found. Creating..."
  django-admin startproject config .
  echo "Project created."
fi

#Create store app if missing
if [ ! -d "store" ]; then
  echo "Creating store app..."
  python manage.py startapp store
  echo "App 'store' created."
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin / admin')
else:
    print('Superuser already exists.')
"

echo "Starting Django..."
exec python manage.py runserver 0.0.0.0:8000