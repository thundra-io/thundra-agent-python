import os

import django
import pytest


@pytest.fixture(autouse=True)
def setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.wrappers.django.app.settings")
    django.setup()
