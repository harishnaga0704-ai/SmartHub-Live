import sys
import os
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from config.wsgi import application

app = application
