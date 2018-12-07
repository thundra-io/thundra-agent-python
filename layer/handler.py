import os
from importlib import import_module
from thundra.thundra_agent import Thundra

thundra = Thundra()
handler_path = os.environ.get('thundra_agent_lambda_handler', 'app.handler')

(module_name, handler_name) = handler_path.rsplit('.', 1)

@thundra
def wrapper(event, context):
    user_module = import_module(module_name)
    user_handler = getattr(user_module, handler_name)
    
    return user_handler(event, context)