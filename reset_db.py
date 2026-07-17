import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

print("Dropping public schema...")
with connection.cursor() as cursor:
    cursor.execute('DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;')
    # We must also grant permissions if needed, but defaults are usually fine

print("Done. Please run python manage.py migrate_schemas --shared manually.")

