import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.mongodb import CommandTracer


def _wrapper(wrapped, instance, args, kwargs):
    event_listeners = list(kwargs.pop('event_listeners', []))
    event_listeners.insert(0, CommandTracer())
    kwargs['event_listeners'] = event_listeners
    wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_MONGO_DISABLE):
        try:
            import pymongo.monitoring
            from bson.json_util import dumps
            wrapt.wrap_function_wrapper(
                'pymongo',
                'MongoClient.__init__',
                _wrapper
            )
        except:
            pass
