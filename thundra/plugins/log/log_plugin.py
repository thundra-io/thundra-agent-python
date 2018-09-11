import uuid

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
            'applicationDomainName': active_span.domain_name,
            'applicationClassName': active_span.class_name,
            'applicationName': function_name,
            'applicationStage':'dev',
            'applicationRuntime':'python',
            'applicationRuntimeVersion':getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
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
        logs.clear()