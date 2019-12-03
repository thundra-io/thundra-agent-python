from __future__ import absolute_import
from importlib import import_module

from thundra import constants
from thundra.config import utils as config_utils

import wrapt

_thundra_instance = None


def _wrapper(wrapped, instance, args, kwargs):
    wrapped = _thundra_instance(wrapped)
    return wrapped(*args, **kwargs)


def patch(thundra_instance):
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_CHALICE_INTEGRATION) and thundra_instance:
        global _thundra_instance
        _thundra_instance = thundra_instance
        try:
            import_module("chalice")
            wrapt.wrap_function_wrapper("chalice", "Chalice.__call__", _wrapper)
        except:
            pass
