from __future__ import absolute_import

import imp
import os

from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names
from catchpoint.catchpoint_agent import Catchpoint

catchpoint = Catchpoint()

handler_found = False
user_handler = None

handler_path = ConfigProvider.get(config_names.CATCHPOINT_LAMBDA_HANDLER, None)
if handler_path is None:
    raise ValueError(
        "No handler specified for \'catchpoint_lambda_handler\' environment variable"
    )
else:
    handler_found = True
    (module_name, handler_name) = handler_path.rsplit('.', 1)
    file_handle, pathname, desc = None, None, None
    try:
        for segment in module_name.split('.'):
            if pathname is not None:
                pathname = [pathname]
            file_handle, pathname, desc = imp.find_module(segment, pathname)
        user_module = imp.load_module(module_name, file_handle, pathname, desc)
        if file_handle is None:
            module_type = desc[2]
            if module_type == imp.C_BUILTIN:
                raise ImportError("Cannot use built-in module {} as a handler module".format(module_name))
        user_handler = getattr(user_module, handler_name)
    finally:
        if file_handle:
            file_handle.close()


def wrapper(event, context):
    global user_handler
    if handler_found and user_handler:
        if not hasattr(user_handler, "catchpoint_wrapper"):
            user_handler = catchpoint(user_handler)
        return user_handler(event, context)
