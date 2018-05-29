import uuid

from thundra import utils, constants
from thundra.plugins.log.thundra_log_handler import logs


class LogPlugin:

    data_format_version = '1.2'

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.common_data = utils.get_common_report_data_from_environment_variable()
        self.log_data = {}

    def before_invocation(self, data):
        context = data['context']
        self.log_data = {
            'id': str(uuid.uuid4()),
            'transactionId': data['transactionId'],
            'rootExecutionAuditContextId': data['contextId'],
            'applicationName': context.function_name,
            'applicationId': self.common_data[constants.AWS_LAMBDA_LOG_STREAM_NAME],
            'applicationVersion': self.common_data[constants.AWS_LAMBDA_FUNCTION_VERSION],
            'applicationProfile': self.common_data[constants.THUNDRA_APPLICATION_PROFILE],
            'applicationType': 'python'
        }

    def after_invocation(self, data):
        reporter = data['reporter']
        for log in logs:
            log.update(self.log_data)
            log_report = {
                'data': log,
                'type': 'MonitoredLog',
                'apiKey': reporter.api_key,
                'dataFormatVersion': LogPlugin.data_format_version
            }
            reporter.add_report(log_report)