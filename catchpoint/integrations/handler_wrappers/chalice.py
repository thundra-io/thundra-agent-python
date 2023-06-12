from __future__ import absolute_import
from importlib import import_module

from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names
import wrapt

_catchpoint_instance = None


def _wrapper(wrapped, _, args, kwargs):
    wrapped = _catchpoint_instance(wrapped)
    return wrapped(*args, **kwargs)


def patch(catchpoint_instance):
    if (not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_CHALICE_DISABLE)) and catchpoint_instance:
        global _catchpoint_instance
        _catchpoint_instance = catchpoint_instance
        try:
            import_module("chalice")
            wrapt.wrap_function_wrapper("chalice", "Chalice.__call__", _wrapper)
        except:
            pass
