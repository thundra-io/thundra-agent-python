import uuid
import sys

from thundra import utils, constants
from thundra.plugins.log.thundra_log_handler import logs
from thundra.opentracing.tracer import ThundraTracer

class LogPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.log_data = {}
        self.tracer = ThundraTracer.getInstance()
        self.scope = None

    def before_invocation(self, data):
        context = data['context']
        logs.clear()
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        active_span = self.tracer.get_active_span()
        self.log_data = {
            'id': str(uuid.uuid4()),
            'type': "Log",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'transactionId': data['transactionId'],
            'tags': {}
        }



    def after_invocation(self, data):
        if 'contextId' in data:
            self.log_data['rootExecutionAuditContextId'] = data['contextId']
        reporter = data['reporter']
        for log in logs:
            log.update(self.log_data)
            log_report = {
                'data': log,
                'type': 'Log',
                'apiKey': reporter.api_key,
                'dataModelVersion': constants.DATA_FORMAT_VERSION
            }
            reporter.add_report(log_report)

        if 'error' in data:
            error = data['error']
            error_type = type(error)
            #Adding tags
            self.log_data['tags']['error'] = True
            self.log_data['tags']['error.kind'] = error_type.__name__
            self.log_data['tags']['error.message'] = str(error)
            if hasattr(error, 'code'):
                self.log_data['tags']['error.code'] = error.code
            if hasattr(error, 'object'):
                self.log_data['tags']['error.object'] = error.object
            if hasattr(error, 'stack'):
                self.log_data['tags']['error.stack'] = error.stack

        logs.clear()