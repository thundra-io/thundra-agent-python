import simplejson as json

from thundra import constants


class InvocationPlugin:

    def __init__(self, plugin_context=None):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.plugin_context = plugin_context

    def before_invocation(self, execution_context):
        executor = self.plugin_context.executor
        if executor:
            executor.start_invocation(self.plugin_context, execution_context)

    def after_invocation(self, execution_context):
        executor = self.plugin_context.executor
        if executor:
            executor.finish_invocation(execution_context)
        report_data = {
            'apiKey': self.plugin_context.api_key,
            'type': 'Invocation',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': execution_context.invocation_data
        }
        execution_context.report(json.loads(json.dumps(report_data)))
