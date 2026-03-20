"""
WSGI entry point untuk deployment dengan Phusion Passenger.

File ini menjaga agar Passenger dapat menemukan project Django dan
menggunakan konfigurasi production secara konsisten.
"""
import sys
import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caera_backend.settings.prod')

from caera_backend.wsgi import application