from thundra import utils, constants
import sys
import thundra.application_support as application_support
import wrapt
from thundra.plugins.log.thundra_log_handler import logs
from thundra.plugins.log.thundra_log_handler import ThundraLogHandler
from thundra.opentracing.tracer import ThundraTracer
import logging


class LogPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.log_data = {}
        self.tracer = ThundraTracer.get_instance()
        disable_prints_to_logs_by_env = utils.get_configuration(constants.THUNDRA_LAMBDA_LOG_CONSOLE_PRINT_DISABLE)
        if not utils.should_disable(disable_prints_to_logs_by_env):
            self.logger = logging.getLogger('STDOUT')
            self.handler = ThundraLogHandler()
            self.logger.addHandler(self.handler)
            self.logger.setLevel(logging.INFO)
            self.handler.setLevel(logging.INFO)
            self.logger.propagate = False
            wrapt.wrap_function_wrapper(
                'builtins',
                'print',
                self._wrapper
            )

    def _wrapper(self, wrapped, instance, args, kwargs):
        try:
            wrapped(*args, **kwargs)
            self.logger.info(str(args[0]))
        except:
            pass

    def before_invocation(self, plugin_context):
        logs.clear()

        context = plugin_context['context']
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        self.log_data = {
            'type': "Log",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME,
            'applicationClassName': constants.AWS_LAMBDA_APPLICATION_CLASS_NAME,
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'traceId': plugin_context.get('trace_id', ""),
            'transactionId': plugin_context.get('transaction_id', context.aws_request_id),
            'tags': {}
        }

    def after_invocation(self, plugin_context):
        context = plugin_context['context']

        #### ADDING TAGS ####
        self.log_data['applicationTags'] = application_support.get_application_tags()
        self.log_data['tags']['aws.region'] = utils.get_aws_region_from_arn(getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.log_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        self.log_data['tags']['aws.lambda.arn'] = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)
        self.log_data['tags']['aws.lambda.memory.limit'] = getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None)
        self.log_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None)
        self.log_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)

        if 'error' in plugin_context:
            error = plugin_context['error']
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

        reporter = plugin_context['reporter']
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
