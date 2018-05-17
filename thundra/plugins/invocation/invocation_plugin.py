import time
import uuid

from thundra import constants, utils
import json

class InvocationPlugin:
    data_format_version = '1.2'
    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.common_data = utils.get_common_report_data_from_environment_variable()
        self.invocation_data = {}

    def before_invocation(self, data):
        if constants.REQUEST_COUNT > 0:
            InvocationPlugin.IS_COLD_START = False

        context = data['context']
        self.start_time = time.time() * 1000
        self.invocation_data = {
            'id': str(uuid.uuid4()),
            'transactionId': data['transactionId'],
            'applicationName': context.function_name,
            'applicationId': self.common_data[constants.AWS_LAMBDA_LOG_STREAM_NAME],
            'applicationVersion': self.common_data[constants.AWS_LAMBDA_FUNCTION_VERSION],
            'applicationProfile': self.common_data[constants.THUNDRA_APPLICATION_PROFILE],
            'applicationType': 'python',
            'duration': None,
            'startTimestamp': int(self.start_time),
            'endTimestamp': None,
            'erroneous': False,
            'errorType': '',
            'errorMessage': '',
            'coldStart': InvocationPlugin.IS_COLD_START,
            'timeout': False,
            'region': self.common_data[constants.AWS_REGION],
            'memorySize': int(context.memory_limit_in_mb)

        }
        InvocationPlugin.IS_COLD_START = False

    def after_invocation(self, data):
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            self.invocation_data['erroneous'] = True
            self.invocation_data['errorType'] = error_type.__name__
            self.invocation_data['errorMessage'] = str(error)

        self.end_time = time.time() * 1000
        duration = self.end_time - self.start_time
        self.invocation_data['duration'] = int(duration)
        self.invocation_data['endTimestamp'] = int(self.end_time)

        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'InvocationData',
            'dataFormatVersion': InvocationPlugin.data_format_version,
            'data': self.invocation_data
        }
        reporter.add_report(json.loads(json.dumps(report_data)))
