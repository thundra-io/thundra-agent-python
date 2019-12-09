import abc
import time
import uuid
import simplejson as json
from thundra import constants, utils
from thundra import application_support
from thundra.plugins.invocation import invocation_support
from thundra.plugins.invocation import invocation_trace_support


class BaseInvocationPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.invocation_data = {}

    def before_invocation(self, plugin_context):
        self.set_start_time(plugin_context)

        plugin_context['transaction_id'] = plugin_context.get('transaction_id', str(uuid.uuid4()))
        self.invocation_data = {
            'id': str(uuid.uuid4()),
            'type': "Invocation",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': plugin_context.get('trace_id', ""),
            'transactionId': plugin_context.get('transaction_id'),
            'spanId': plugin_context.get('span_id', ""),
            'applicationPlatform': constants.CONTEXT_APPLICATION_PLATFORM,
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
            'userTags': {}
        }

        # Add application related data
        application_info = application_support.get_application_info()
        self.invocation_data.update(application_info)

        self.before_invocation_hook(plugin_context)

    def set_start_time(self, plugin_context):
        if 'start_time' in plugin_context:
            self.start_time = plugin_context['start_time']
        else:
            self.start_time = int(time.time() * 1000)
            plugin_context['start_time'] = self.start_time

    def set_end_time(self, plugin_context):
        if 'end_time' in plugin_context:
            self.end_time = plugin_context['end_time']
        else:
            self.end_time = int(time.time() * 1000)
            plugin_context['end_time'] = self.end_time

    def set_error(self, error):
        error_type = type(error)
        self.invocation_data['erroneous'] = True
        self.invocation_data['errorType'] = error_type.__name__
        self.invocation_data['errorMessage'] = str(error)
        if hasattr(error, 'code'):
            self.invocation_data['errorCode'] = error.code

    def after_invocation(self, plugin_context):
        self.set_end_time(plugin_context)

        # Add user tags
        self.invocation_data['userTags'].update(invocation_support.get_tags())

        # Add agent tags
        self.invocation_data['tags'].update(invocation_support.get_agent_tags())

        # Get resources
        resources = invocation_trace_support.get_resources(plugin_context)
        self.invocation_data.update(resources)

        # Get incoming trace links
        incoming_trace_links = invocation_trace_support.get_incoming_trace_links()
        self.invocation_data.update(incoming_trace_links)

        # Get outgoing trace links
        outgoing_trace_links = invocation_trace_support.get_outgoing_trace_links()
        self.invocation_data.update(outgoing_trace_links)

        # Check errors
        user_error = invocation_support.get_error()
        if 'error' in plugin_context:
            error = plugin_context['error']
            self.set_error(error)
        elif user_error:
            self.set_error(user_error)

        self.invocation_data['timeout'] = plugin_context.get('timeout', False)

        duration = self.end_time - self.start_time
        self.invocation_data['duration'] = int(duration)
        self.invocation_data['finishTimestamp'] = int(self.end_time)

        self.after_invocation_hook(plugin_context)

        invocation_support.clear()
        invocation_trace_support.clear()
        self.report(plugin_context)

    def report(self, plugin_context):
        reporter = plugin_context['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Invocation',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.invocation_data
        }
        reporter.add_report(json.loads(json.dumps(report_data)))

    @abc.abstractmethod
    def before_invocation_hook(self, plugin_context):
        pass

    @abc.abstractmethod
    def after_invocation_hook(self, plugin_context):
        pass
