import os
import sys
from pathlib import Path

# Ensure the project root is on the Python path so Django can find
# the "config" package and the "shop" app.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Run collectstatic on cold start so WhiteNoise can find the files.
from django.core.management import call_command
import django
django.setup()

STATICFILES_DIR = PROJECT_ROOT / "staticfiles"
if not STATICFILES_DIR.exists():
    try:
        call_command("collectstatic", "--noinput", verbosity=0)
    except Exception:
        pass

# Run migrations to /tmp SQLite on cold start
if os.getenv("VERCEL"):
    try:
        call_command("migrate", "--noinput", verbosity=0)
    except Exception:
        pass

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
