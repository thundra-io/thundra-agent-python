from thundra.plugins.aws_xray.xray_plugin import AWSXRayPlugin
from thundra.listeners.aws_xray_listeners import AWSXRayListener
from thundra.plugins.trace import trace_support


def test_xray_plugin_initialization(handler_with_xray):
    thundra, _ = handler_with_xray
    found = False
    for plugin in thundra.plugins:
        if isinstance(plugin, AWSXRayPlugin):
            xray_plugin = plugin
            found = True
            break
    
    assert found
    
    if AWSXRayListener.xray_available():
        listener = trace_support.get_span_listeners()[-1]
        assert isinstance(listener, AWSXRayListener)
    
    trace_support.clear_span_listeners()
