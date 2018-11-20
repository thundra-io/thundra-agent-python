from __future__ import absolute_import
import wrapt
from thundra.integrations.modules.generic_wrapper import wrapper
from thundra.integrations.events.requests import RequestsEventFactory

def _wrapper(wrapped, instance, args, kwargs):
    return wrapper(RequestsEventFactory, wrapped, instance, args, kwargs)

def patch():
    wrapt.wrap_function_wrapper(
        'requests',
        'Session.send',
        _wrapper
    )