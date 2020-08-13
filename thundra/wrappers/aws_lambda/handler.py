from __future__ import absolute_import

import imp
import os

from thundra.thundra_agent import Thundra

thundra = Thundra()

handler_found = False
user_handler = None
handler_path = os.environ.get('thundra_agent_lambda_handler', None)
if handler_path is None:
    raise ValueError(
        "No handler specified for \'thundra_agent_lambda_handler\' environment variable"
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
        if not hasattr(user_handler, "thundra_wrapper"):
            user_handler = thundra(user_handler)
        return user_handler(event, context)
