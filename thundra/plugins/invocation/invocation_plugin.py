import time
import uuid
import sys

import json
from thundra import constants, utils
import thundra.plugins.invocation.invocation_support as invocation_support
import thundra.application_support as application_support


class InvocationPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.invocation_data = {}

    def before_invocation(self, plugin_context):
        context = plugin_context['context']
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        invocation_support.clear()
        self.start_time = int(time.time() * 1000)

        self.invocation_data = {
            'id': str(uuid.uuid4()),
            'type': "Invocation",
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
            'spanId': plugin_context.get('span_id', ""),
            'functionPlatform': constants.CONTEXT_FUNCTION_PLATFORM,
            'functionName': getattr(context, 'function_name', None),
            'functionRegion': utils.get_configuration(constants.AWS_REGION, default=''),
            'duration': None, 
            'startTimestamp': int(self.start_time),
            'finishTimestamp': None,
            'erroneous': False,
            'errorType': '',
            'errorMessage': '',
            'errorCode': -1,
            'coldStart': constants.REQUEST_COUNT == 1,
            'timeout': False,
            'tags': {},
        }

    def after_invocation(self, plugin_context):
        total_mem, used_mem = utils.process_memory_usage()
        used_mem_in_mb = used_mem / 1048576
        self.end_time = time.time() * 1000
        context = plugin_context['context']
        #### ADDING USER TAGS ####
        self.invocation_data['tags'] = invocation_support.get_tags_dict()

        #### ERROR ####
        if 'error' in plugin_context:
            error = plugin_context['error']
            error_type = type(error)
            self.invocation_data['erroneous'] = True
            self.invocation_data['errorType'] = error_type.__name__
            self.invocation_data['errorMessage'] = str(error)
            if hasattr(error, 'code'):
                self.invocation_data['errorCode'] = error.code

            # Adding tags
            self.invocation_data['tags']['error'] = True
            self.invocation_data['tags']['error.kind'] = error_type.__name__
            self.invocation_data['tags']['error.message'] = str(error)
            if hasattr(error, 'code'):
                self.invocation_data['tags']['error.code'] = error.code
            if hasattr(error, 'object'):
                self.invocation_data['tags']['error.object'] = error.object
            if hasattr(error, 'stack'):
                self.invocation_data['tags']['error.stack'] = error.stack

        self.invocation_data['timeout'] = plugin_context.get('timeout', False)

        duration = self.end_time - self.start_time
        self.invocation_data['duration'] = int(duration)
        self.invocation_data['finishTimestamp'] = int(self.end_time)

        #### ADDING AWS TAGS ####
        self.invocation_data['applicationTags'] = application_support.get_application_tags()
        self.invocation_data['tags']['aws.region'] = utils.get_aws_region_from_arn(getattr (context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.invocation_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        self.invocation_data['tags']['aws.lambda.arn'] = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)
        self.invocation_data['tags']['aws.lambda.memory_limit'] = getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None)
        self.invocation_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None)
        self.invocation_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
        self.invocation_data['tags']['aws.lambda.invocation.cold_start'] = self.invocation_data['coldStart']
        self.invocation_data['tags']['aws.lambda.invocation.timeout'] = plugin_context.get('timeout', False)
        self.invocation_data['tags']['aws.lambda.invocation.request_id'] = getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None)
        self.invocation_data['tags']['aws.lambda.invocation.memory_usage'] = used_mem_in_mb

        reporter = plugin_context['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Invocation',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.invocation_data
        }
        reporter.add_report(json.loads(json.dumps(report_data)))
        invocation_support.clear()
