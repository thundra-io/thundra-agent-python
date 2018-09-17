import time
import uuid
import sys

from thundra import constants, utils
import json
from thundra.opentracing.tracer import ThundraTracer

class InvocationPlugin:

    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.invocation_data = {}
        self.tracer = ThundraTracer()

    def before_invocation(self, data):
        if constants.REQUEST_COUNT > 0:
            InvocationPlugin.IS_COLD_START = False

        context = data['context']
        memory_size = getattr(context, 'memory_limit_in_mb', None)
        self.start_time = time.time() * 1000

        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)


        self.start_time = int(time.time() * 1000)
        active_span = self.tracer.get_active_span()

        self.invocation_data = {
            'id': str(uuid.uuid4()),
            'type': "Invocation",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': active_span.domain_name if active_span is not None else '',
            'applicationClassName': active_span.class_name if active_span is not None else '',
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'traceId': 'root_trace_id_{}'.format(str(uuid.uuid4())),
            'transactionId': data['transactionId'],
            'spanId': 'root_span_id{}'.format(str(uuid.uuid4())),
            'functionPlatform': 'python', #old name: applicationType
            'functionName': getattr(context, 'function_name', None), #old name: applicationName
            'functionRegion': utils.get_environment_variable(constants.AWS_REGION, default=''), #old name: region
            'duration': None, 
            'startTimestamp': int(self.start_time),
            'finishTimestamp': None, #old name: endTimestamp
            'erroneous': False,
            'errorType': '',
            'errorMessage': '',
            'errorCode': -1, #new addition
            'coldStart': InvocationPlugin.IS_COLD_START,
            'timeout': False,
            'tags': {}, #new addition
            #'memorySize': int(memory_size) if memory_size is not None else None,
        }
        InvocationPlugin.IS_COLD_START = False

    def after_invocation(self, data):


        context = data['context']
        active_span = self.tracer.get_active_span()

        self.invocation_data['traceId']: active_span.trace_id if active_span is not None else ''
        self.invocation_data['transactionId']: data['transactionId']
        self.invocation_data['spanId']: active_span.span_id if active_span is not None else ''

        #### ERROR ####
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            self.invocation_data['erroneous'] = True
            self.invocation_data['errorType'] = error_type.__name__
            self.invocation_data['errorMessage'] = str(error)
            if hasattr(error, 'code'):
                self.invocation_data['errorCode'] = error.code

            #Adding tags
            self.invocation_data['tags']['error'] = True
            self.invocation_data['tags']['error.kind'] = error_type.__name__
            self.invocation_data['tags']['error.message'] = str(error)
            if hasattr(error, 'code'):
                self.invocation_data['tags']['error.code'] = error.code
            if hasattr(error, 'object'):
                self.invocation_data['tags']['error.object'] = error.object
            if hasattr(error, 'stack'):
                self.invocation_data['tags']['error.stack'] = error.stack

        self.invocation_data['timeout'] = data.get('timeout', False)

        self.end_time = time.time() * 1000
        duration = self.end_time - self.start_time
        self.invocation_data['duration'] = int(duration)
        self.invocation_data['finishTimestamp'] = int(self.end_time) # change: endTimestamp -> finishTimestamp

        #### ADDING TAGS ####
        default = {}
        self.invocation_data['tags']['aws.region'] = utils.get_aws_region_from_arn(getattr (context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.invocation_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        self.invocation_data['tags']['aws.lambda.arn'] = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)
        self.invocation_data['tags']['aws.lambda.memory.limit'] = getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None)
        self.invocation_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None)
        self.invocation_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
        self.invocation_data['tags']['aws.lambda.invocation.cold_start'] = InvocationPlugin.IS_COLD_START
        self.invocation_data['tags']['aws.lambda.invocation.timeout'] = data.get('timeout', False)
        self.invocation_data['tags']['aws.lambda.invocation.request_id'] = getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None)
        self.invocation_data['tags']['aws.lambda.invocation.request'] = data.get('event', default)
        self.invocation_data['tags']['aws.lambda.invocation.response'] = data.get('response', default)

        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Invocation',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.invocation_data
        }
        reporter.add_report(json.loads(json.dumps(report_data)))
