from __future__ import absolute_import
import os
from importlib import import_module
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
    user_module = import_module(module_name)
    user_handler = getattr(user_module, handler_name)

def wrapper(event, context):
    global user_handler
    if handler_found and user_handler:
        if not hasattr(user_handler, "thundra_wrapper"):
            user_handler = thundra(user_handler)
        return user_handler(event, context)