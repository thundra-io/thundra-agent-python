from __future__ import absolute_import
import wrapt
from thundra.utils import is_excluded_url
from thundra.integrations.modules.generic_wrapper import wrapper
from thundra.integrations.events.requests import RequestsEventFactory

def _wrapper(wrapped, instance, args, kwargs):
    prepared_request = args[0]

    if is_excluded_url(prepared_request.url):
        return wrapped(*args, **kwargs)

    return wrapper(RequestsEventFactory, wrapped, instance, args, kwargs)

def patch():
    wrapt.wrap_function_wrapper(
        'requests',
        'Session.send',
        _wrapper
    )