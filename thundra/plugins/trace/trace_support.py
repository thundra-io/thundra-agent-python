import os
import re
import thundra.utils as utils
from thundra.listeners import ThundraSpanListener
from thundra.constants import THUNDRA_LAMBDA_SPAN_LISTENER

SPAN_LISTENERS = {
    sl_class.__name__: sl_class 
        for sl_class in ThundraSpanListener.__subclasses__()
}

_span_listeners = []

reg_ex = r'(\w+)\[(.*)\]'
p = re.compile(reg_ex)

for k, v in os.environ.items():
    if k.startswith(THUNDRA_LAMBDA_SPAN_LISTENER):
        m = p.match(v)
        print("{} -> {}".format(SPAN_LISTENERS.get(m.group(1)), m.group(2)))


def get_span_listeners():
    return _span_listeners

def register_span_listener(listener):
    _span_listeners.append(listener)

def clear_span_listeners():
    _span_listeners.clear()
