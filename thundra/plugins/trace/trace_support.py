import base64
import json
import logging
import re
from gzip import GzipFile

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from thundra.listeners import ThundraSpanListener

from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

logger = logging.getLogger(__name__)

_active_span_listeners = []
_sampler = None

SPAN_LISTENERS = {
    sl_class.__name__: sl_class
    for sl_class in ThundraSpanListener.__subclasses__()
}

# To match span listener class type and it's arguments as two groups
r1 = r'(\w+)\[(.*)\]'
# To match each argument key value pair in arguments list
r2 = r'[\w.]+=[\w.\!\?\-\"\'\:\(\) ]*'
# Compile reg exs
p1 = re.compile(r1)
p2 = re.compile(r2)


def get_span_listeners():
    return _active_span_listeners


def register_span_listener(listener):
    _active_span_listeners.append(listener)


def clear_span_listeners():
    global _active_span_listeners
    _active_span_listeners = []


def _get_sl_class(sl_class_name):
    sl_class = None
    if sl_class_name is not None:
        try:
            sl_class = SPAN_LISTENERS[sl_class_name]
        except KeyError:
            logger.error('given span listener class %s is not found', sl_class_name)
    return sl_class


def _parse_span_listeners():
    # Clear before parsing to prevent appending duplicate span listeners
    clear_span_listeners()
    # Add span listeners configured using environment variables
    for env_k in ConfigProvider.configs:
        env_v = ConfigProvider.get(env_k)
        if env_k.startswith(config_names.THUNDRA_TRACE_SPAN_LISTENERCONFIG):
            try:
                # Not in JSON format. Should be zipped + encoded. Decode + unzip it
                if not env_v.startswith('{'):
                    compressed_env = base64.b64decode(env_v)
                    env_v = str(GzipFile(fileobj=BytesIO(compressed_env)).read(), 'utf-8')
                span_listener_config_json = json.loads(env_v)

                listener_type = span_listener_config_json.get("type")
                if not listener_type:
                    raise Exception("type property is mandatory in " + env_k + " configuration")

                listener_config = span_listener_config_json.get("config")
                if not listener_config:
                    raise Exception("config property is mandatory in " + env_k + " configuration")

                span_listener_class = _get_sl_class(listener_type)

                if span_listener_class is not None:
                    span_listener = span_listener_class.from_config(listener_config)
                    register_span_listener(span_listener)

            except Exception as e:
                logger.error(("couldn't parse environment variable %s "
                              "to create a span listener"), env_k)


# Parse span listeners from environment variables
_parse_span_listeners()


def get_sampler():
    return _sampler


def set_sampler(sampler):
    global _sampler
    _sampler = sampler
