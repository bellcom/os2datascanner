"""
WSGI config for webscanner project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webscanner.settings")

site_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
)
lib_path = 'python-env/lib/python3.6/site-packages'
lib_path1 = 'python-env/lib/python3.5/site-packages'

install_dir = os.path.abspath(os.path.join(site_dir, '..'))
lib_dir = os.path.join(install_dir, lib_path)
lib_dir1 = os.path.join(install_dir, lib_path1)
webscanner_dir = os.path.join(install_dir, 'django-os2webscanner')

sys.path[0:0] = [site_dir, lib_dir, lib_dir1, webscanner_dir]

try:
    import os2webscanner
except Exception:
    raise RuntimeError("Path: " + str(sys.path))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
