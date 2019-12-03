from __future__ import absolute_import
import thundra.lambda_support as lambda_support

lambda_support.initialize_properties()

from importlib import import_module
from thundra.config import utils as config_utils
import thundra.integrations.modules as integrations


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


if not config_utils.get_bool_property("thundra_agent_disable"):
    patch_modules()
