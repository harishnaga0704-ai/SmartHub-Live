import os
from pathlib import Path
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    call_command('migrate', '--noinput', verbosity=0)
except Exception as e:
    print(f"Startup migration notice: {e}")

from config.wsgi import application as app
