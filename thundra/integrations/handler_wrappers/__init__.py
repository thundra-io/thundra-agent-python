from __future__ import absolute_import

import os
import traceback
from importlib import import_module

MODULES = {}
IGNORE_MODULES = ('__init__',)
PYTHON_EXTENSIONS = ('.py', '.pyc')

for module_name in os.listdir(os.path.dirname(__file__)):
    filename, ext = os.path.splitext(module_name)
    if filename in IGNORE_MODULES or ext not in PYTHON_EXTENSIONS:
        continue
    try:
        imported = import_module(".{}".format(filename), __name__)
        MODULES[filename] = imported
    except ImportError:
        traceback.print_exc()


def _import_exists(module_name):
    try:
        import_module(module_name)
        return True
    except ImportError:
        return False


def patch_modules(thundra_instance):
    for module_name, module in MODULES.items():
        if _import_exists(module_name):
            module.patch(thundra_instance)
