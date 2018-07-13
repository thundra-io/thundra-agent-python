import time
import uuid

from thundra import constants, utils
import json

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

    def before_invocation(self, data):
        if constants.REQUEST_COUNT > 0:
            InvocationPlugin.IS_COLD_START = False

        context = data['context']
        memory_size = getattr(context, 'memory_limit_in_mb', None)
        self.start_time = time.time() * 1000
        self.invocation_data = {
            'id': str(uuid.uuid4()),
            'transactionId': data['transactionId'],
            'applicationName': getattr(context, 'function_name', None),
            'applicationId': utils.get_application_id(context),
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationProfile': utils.get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE, default=''),
            'applicationType': 'python',
            'duration': None,
            'startTimestamp': int(self.start_time),
            'endTimestamp': None,
            'erroneous': False,
            'errorType': '',
            'errorMessage': '',
            'coldStart': InvocationPlugin.IS_COLD_START,
            'timeout': False,
            'region': utils.get_environment_variable(constants.AWS_REGION, default=''),
            'memorySize': int(memory_size) if memory_size is not None else None

        }
        InvocationPlugin.IS_COLD_START = False

    def after_invocation(self, data):
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            self.invocation_data['erroneous'] = True
            self.invocation_data['errorType'] = error_type.__name__
            self.invocation_data['errorMessage'] = str(error)

        self.invocation_data['timeout'] = data.get('timeout', False)

        self.end_time = time.time() * 1000
        duration = self.end_time - self.start_time
        self.invocation_data['duration'] = int(duration)
        self.invocation_data['endTimestamp'] = int(self.end_time)

        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'InvocationData',
            'dataFormatVersion': constants.DATA_FORMAT_VERSION,
            'data': self.invocation_data
        }
        reporter.add_report(json.loads(json.dumps(report_data)))
