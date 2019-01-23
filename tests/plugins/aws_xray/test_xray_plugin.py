from thundra.plugins.aws_xray.xray_plugin import AWSXRayPlugin
from thundra.listeners.aws_xray_listeners import AWSXrayListener
from thundra.plugins.trace import trace_support


def test_xray_plugin_initialization(handler_with_xray):
    thundra, handler = handler_with_xray
    found = False
    tracer = AWSXRayPlugin().tracer
    for plugin in thundra.plugins:
        if isinstance(plugin, AWSXRayPlugin):
            xray_plugin = plugin
            found = True
    assert found
    trace_support.clear_span_listeners()
    tracer.clear()


def test_xray_data():
    tracer = AWSXRayPlugin().tracer
    listener = trace_support.get_span_listeners()[-1]
    assert isinstance(listener, AWSXrayListener)
    trace_support.clear_span_listeners()
    tracer.clear()


