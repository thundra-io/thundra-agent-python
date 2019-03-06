from __future__ import absolute_import
import wrapt
from thundra import utils, config


def _wrapper(wrapped, instance, args, kwargs):
    print("elastic search call has been received")
    return wrapped(*args, **kwargs)

def patch():
    wrapt.wrap_function_wrapper(
        'elasticsearch',
        'transport.Transport.perform_request',
        _wrapper
    )
