from __future__ import absolute_import
from importlib import import_module
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
import thundra.integrations.modules as integrations
from thundra import _version

__version__ = _version.__version__

def _import_exists(module_name):
    try:
        import_module(module_name)
        return True
    except ImportError:
        return False

def patch_modules():
    for module_name, module in integrations.MODULES.items():
        if _import_exists(module_name):
            module.patch()

if not ConfigProvider.get(config_names.THUNDRA_DISABLE):
    patch_modules()
