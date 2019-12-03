import wrapt

from thundra.integrations.mongodb import CommandTracer
from thundra.config import utils as config_utils
from thundra import constants


def _wrapper(wrapped, instance, args, kwargs):
    event_listeners = list(kwargs.pop('event_listeners', []))
    event_listeners.insert(0, CommandTracer())
    kwargs['event_listeners'] = event_listeners
    wrapped(*args, **kwargs)


def patch():
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_MONGO_INTEGRATION):
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
