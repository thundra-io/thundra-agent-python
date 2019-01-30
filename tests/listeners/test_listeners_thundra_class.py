import logging

from thundra.thundra_agent import Thundra
from tests.listeners.test_xray_listener_class import AWSXRayListenerTesting
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.aws_xray.xray_plugin import AWSXRayPlugin

logger = logging.getLogger(__name__)


class ThundraForListeners(Thundra):

    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=False,
                 disable_log=False):
        super(ThundraForListeners, self).__init__(api_key='test_api_key',
                                                  disable_trace=False,
                                                  disable_metric=True,
                                                  disable_log=False)

        tracer = ThundraTracer.get_instance()
        tracer.clear()
        self.plugins.pop(-1)
        self.plugins.append(AWSXRayPlugin(AWSXRayListenerTesting()))

    def __call__(self, original_func):
        return super(ThundraForListeners, self).__call__(original_func)

    call = __call__

    def execute_hook(self, name, data):
        super(ThundraForListeners, self).execute_hook(name, data)

    def check_and_handle_warmup_request(self, event):
        return super(ThundraForListeners, self).check_and_handle_warmup_request(event)

    def timeout_handler(self, signum, frame):
        super(ThundraForListeners, self).timeout_handler(signum, frame)

    def prepare_and_send_reports(self):
        super(ThundraForListeners, self).prepare_and_send_reports()
