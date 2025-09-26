"""Settings package entry point.

Defaults to development settings unless ``DJANGO_SETTINGS_MODULE`` overrides it.
"""

import os

default_settings_module = "api_core.settings.dev"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings_module)


