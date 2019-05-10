import wrapt

from thundra import constants, config
from thundra.integrations.mongo import CommandTracer


def _wrapper(wrapped, instance, args, kwargs):
    event_listeners = list(kwargs.pop('event_listeners', []))
    event_listeners.insert(0, CommandTracer())
    kwargs['event_listeners'] = event_listeners
    wrapped(*args, **kwargs)


def patch():
    if not config.mongo_integration_disabled():
        try:
            import pymongo.monitoring
            wrapt.wrap_function_wrapper(
                'pymongo',
                'MongoClient.__init__',
                _wrapper
            )
        except:
            pass
