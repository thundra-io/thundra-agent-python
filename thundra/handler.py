import os
from importlib import import_module
from thundra.thundra_agent import Thundra

thundra = Thundra()

handler_found = False
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

@thundra
def wrapper(event, context):
    if handler_found:
        return user_handler(event, context)
