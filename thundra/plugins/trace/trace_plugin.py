import time
import uuid

import thundra.utils as utils
from thundra import constants


class TracePlugin:

    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.trace_data = {}

    def before_invocation(self, data):

        if constants.REQUEST_COUNT > 0:
            TracePlugin.IS_COLD_START = False
        context = data['context']
        event = data['event']

        context_id = str(uuid.uuid4())
        data['contextId'] = context_id

        self.start_time = time.time() * 1000
        self.trace_data = {
            'id': str(uuid.uuid4()),
            'transactionId': data['transactionId'],
            'applicationName': getattr(context, constants.CONTEXT_FUNCTION_NAME, None),
            'applicationId': utils.get_application_id(context),
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationProfile': utils.get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE, ''),
            'applicationType': 'python',
            'duration': None,
            'startTimestamp': int(self.start_time),
            'endTimestamp': None,
            'errors': [],
            'thrownError': None,
            'contextType': 'ExecutionContext',
            'contextName': getattr(context, constants.CONTEXT_FUNCTION_NAME, None),
            'contextId': context_id,
            'auditInfo': {
                'contextName': getattr(context, constants.CONTEXT_FUNCTION_NAME, None),
                'id': context_id,
                'openTimestamp': int(self.start_time),
                'closeTimestamp': None,
                'errors': [],
                'thrownError': None
            },
            'properties': {
                'request': event if data['request_skipped'] is False else None,
                'response': None,
                'coldStart': 'true' if TracePlugin.IS_COLD_START else 'false',
                'functionRegion': utils.get_environment_variable(constants.AWS_REGION, ''),
                'functionMemoryLimitInMB': getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None),
                'logGroupName': getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None),
                'logStreamName': getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None),
                'functionARN': getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN),
                'requestId': getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None)
            }

        }
        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            exception = {
                'errorType': error_type.__name__,
                'errorMessage': str(error),
                'args': error.args,
                'cause': error.__cause__
            }
            self.trace_data['errors'].append(error_type.__name__)
            self.trace_data['thrownError'] = error_type.__name__
            self.trace_data['auditInfo']['errors'].append(exception)
            self.trace_data['auditInfo']['thrownError'] = exception

        if 'response' in data:
            self.trace_data['properties']['response'] = data['response']
        self.end_time = time.time() * 1000
        duration = self.end_time - self.start_time
        self.trace_data['duration'] = int(duration)
        self.trace_data['endTimestamp'] = int(self.end_time)
        self.trace_data['auditInfo']['closeTimestamp'] = int(self.end_time)

        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'AuditData',
            'dataFormatVersion': constants.DATA_FORMAT_VERSION,
            'data': self.trace_data
        }
        reporter.add_report(report_data)



