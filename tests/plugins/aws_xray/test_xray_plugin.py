from thundra.plugins.aws_xray.xray_plugin import AWSXRayPlugin
import os
from thundra import constants


def test_xray_plugin_initialization(handler, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler
    found = False
    print(thundra.plugins)
    for plugin in thundra.plugins:
        if isinstance(plugin, AWSXRayPlugin):
            xray_plugin = plugin
            found = True

    assert found == True



