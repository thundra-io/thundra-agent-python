from thundra import utils, constants
from thundra.plugins.log.thundra_log_handler import logs


class LogPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.log_data = {}

    def before_invocation(self, data):
        context = data['context']
        logs.clear()
        self.log_data = {
            'transactionId': data['transactionId'],
            'applicationName': getattr(context, 'function_name', None),
            'applicationId': utils.get_application_id(context),
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationProfile': utils.get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE, ''),
            'applicationType': 'python'
        }

    def after_invocation(self, data):
        if 'contextId' in data:
            self.log_data['rootExecutionAuditContextId'] = data['contextId']
        reporter = data['reporter']
        for log in logs:
            log.update(self.log_data)
            log_report = {
                'data': log,
                'type': 'MonitoredLog',
                'apiKey': reporter.api_key,
                'dataFormatVersion': constants.DATA_FORMAT_VERSION
            }
            reporter.add_report(log_report)
        logs.clear()