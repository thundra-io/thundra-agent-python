import os
import re
import logging
import thundra.utils as utils
from thundra.listeners import ThundraSpanListener
from thundra.constants import THUNDRA_LAMBDA_SPAN_LISTENER

logger = logging.getLogger(__name__)

_active_span_listeners = []

SPAN_LISTENERS = {
    sl_class.__name__: sl_class 
    for sl_class in ThundraSpanListener.__subclasses__()
}

# To match span listener class type and it's arguments as two groups
r1 = r'(\w+)\[(.*)\]'
# To match each argument key value pair in arguments list
r2 = r'[\w.]+=[\w\-\"\' ]*'
# Compile reg exs
p1 = re.compile(r1)
p2 = re.compile(r2)

for env_k, env_v in os.environ.items():
    if env_k.startswith(THUNDRA_LAMBDA_SPAN_LISTENER):
        m = p1.match(env_v)
        if m is not None:
            try:
                sl_class_name = m.group(1)
                config_str = m.group(2)
            except IndexError as e:
                logger.warning(e)

            config = {}
            kv_pairs = p2.findall(config_str)
            for kv in kv_pairs:
                [k, v] = kv.split('=')
                config[k] = v
            
            sl_class = SPAN_LISTENERS.get(sl_class_name)
            sl = sl_class.from_config(config)
            _active_span_listeners.append(sl)
                
def get_span_listeners():
    return _active_span_listeners

def register_span_listener(listener):
    _active_span_listeners.append(listener)

def clear_span_listeners():
    _active_span_listeners.clear()
