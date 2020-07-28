from __future__ import absolute_import
from importlib import import_module

from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
import wrapt

_thundra_instance = None


def _wrapper(wrapped, _, args, kwargs):
    wrapped = _thundra_instance(wrapped)
    return wrapped(*args, **kwargs)


def patch(thundra_instance):
    if (not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_CHALICE_DISABLE)) and thundra_instance:
        global _thundra_instance
        _thundra_instance = thundra_instance
        try:
            import_module("chalice")
            wrapt.wrap_function_wrapper("chalice", "Chalice.__call__", _wrapper)
        except:
            pass
