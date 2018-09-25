from thundra import utils, constants
import sys

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
            context = data['context']

            #### ADDING TAGS ####
            self.log_data['tags']['aws.region'] = utils.get_aws_region_from_arn(getattr (context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
            self.log_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME,
                                                               None)
            self.log_data['tags']['aws.lambda.arn'] = getattr(context,
                                                              constants.CONTEXT_INVOKED_FUNCTION_ARN, None)
            self.log_data['tags']['aws.lambda.memory.limit'] = getattr(context,
                                                                       constants.CONTEXT_MEMORY_LIMIT_IN_MB,
                                                                       None)
            self.log_data['tags']['aws.lambda.log_group_name'] = getattr(context,
                                                                         constants.CONTEXT_LOG_GROUP_NAME,
                                                                         None)
            self.log_data['tags']['aws.lambda.log_stream_name'] = getattr(context,
                                                                          constants.CONTEXT_LOG_STREAM_NAME,
                                                                          None)
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
            # Adding tags
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
