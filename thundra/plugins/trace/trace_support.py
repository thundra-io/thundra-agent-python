import os
import re
import logging
from thundra import constants
from thundra import config as thundra_config
from thundra.listeners import ThundraSpanListener, AWSXRayListener

logger = logging.getLogger(__name__)

_active_span_listeners = []

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
    _active_span_listeners.clear()

def _parse_config(config_str):
    config = {}
    if config_str is not None:
        kv_pairs = p2.findall(config_str)
        for kv in kv_pairs:
            [k, v] = kv.split('=')
            config[k] = v
    
    return config

def _get_sl_class(sl_class_name):
    sl_class = None
    if sl_class_name is not None:
        try:
            sl_class = SPAN_LISTENERS[sl_class_name]
        except KeyError:
            logger.error('given span listener class %s is not found', sl_class_name)
    return sl_class

def _get_class_and_config_parts(env_v):
    m = p1.match(env_v)
    if m is not None:
        try:
            sl_class_name = m.group(1)
            config_str = m.group(2)
            return (sl_class_name, config_str)
        except IndexError as e:
            logger.error(("couldn't parse thundra span "
                          "listener environment variable: %s"), e)
    
    return (None, None)
    


def parse_span_listeners():
    # Clear before parsing to prevent appending duplicate span listeners
    clear_span_listeners()
    # Add span listeners configured using environment variables
    for env_k, env_v in os.environ.items():
        if env_k.startswith(constants.THUNDRA_LAMBDA_SPAN_LISTENER):
            try:
                sl_class_name, config_str = _get_class_and_config_parts(env_v)

                config = _parse_config(config_str)
                sl_class = _get_sl_class(sl_class_name)
                
                if sl_class is not None:    
                    sl = sl_class.from_config(config)
                    # Register parsed span listener
                    register_span_listener(sl)
            except Exception as e:
                logger.error(("couldn't parse environment variable %s "
                    "to create a span listener"), env_k)
    # Add AWSXRayListener if enabled
    if thundra_config.xray_trace_enabled():
        xray_listener = AWSXRayListener()
        register_span_listener(xray_listener)


# Parse span listeners from environment variables
parse_span_listeners()

