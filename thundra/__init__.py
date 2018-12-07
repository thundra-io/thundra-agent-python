from __future__ import absolute_import
from importlib import import_module
import thundra.integrations.modules as integrations
import thundra.listeners as listeners


def _import_exists(module_name):
    """
    Validates if import module exists
    :param module_name: module name to import
    :return: Bool
    """
    try:
        import_module(module_name)
        return True
    except ImportError:
        return False


for patch_module in integrations.MODULES:
    if _import_exists(patch_module):
        integrations.MODULES[patch_module].patch()
