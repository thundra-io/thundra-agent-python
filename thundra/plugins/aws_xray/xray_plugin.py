from thundra.opentracing.tracer import ThundraTracer
import sys
import thundra.application_support as application_support
from thundra import utils
from thundra import constants
from thundra.listeners.aws_xray_listeners import AWSXRayListener


class AWSXRayPlugin:

    def __init__(self, listener=None):
        if AWSXRayListener.xray_available():
            self.hooks = {
                'before:invocation': self.before_invocation,
                'after:invocation': self.after_invocation
            }
            self.tracer = ThundraTracer.get_instance()
            self.xray_data = {}
            if listener is None:
                self.xray_listener = AWSXRayListener()
            else:
                self.xray_listener = listener
            if self.tracer:
                self.tracer.add_span_listener(self.xray_listener)

    def before_invocation(self, plugin_context):
        context = plugin_context['context']
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        app_tags = application_support.get_application_tags()

        self.xray_data = {
            'applicationId': utils.get_application_id(context),
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': app_tags,
        }

        self.send_data(self.xray_data)

    def after_invocation(self, plugin_context):
        pass

    def send_data(self, data):
        if AWSXRayListener.xray_available():
            self.xray_listener.set_data(data)
