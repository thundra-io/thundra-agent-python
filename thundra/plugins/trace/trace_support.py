from thundra.listeners.error_injector_listener import ErrorInjectorListener

span_listeners = []

def get_span_listeners():
    return span_listeners

def register_span_listener(listener):
    span_listeners.append(listener)

def clear_span_listener():
    span_listeners.clear()