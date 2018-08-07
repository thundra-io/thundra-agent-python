import time
import uuid

import thundra.utils as utils
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer


class TracePlugin:
    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.tracer = ThundraTracer.getInstance()
        self.scope = None
        self.start_time = 0
        self.end_time = 0
        self.trace_data = {}

    def before_invocation(self, data):

        if constants.REQUEST_COUNT > 0:
            TracePlugin.IS_COLD_START = False
        context = data['context']

        context_id = str(uuid.uuid4())
        data['contextId'] = context_id
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        self.start_time = int(time.time() * 1000)
        self.trace_data = {
            'id': str(uuid.uuid4()),
            'transactionId': data['transactionId'],
            'applicationName': function_name,
            'applicationId': utils.get_application_id(context),
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationProfile': utils.get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE, ''),
            'applicationType': 'python',
            'duration': None,
            'startTimestamp': self.start_time,
            'endTimestamp': None,
            'errors': None,
            'thrownError': None,
            'contextType': 'ExecutionContext',
            'contextName': function_name,
            'contextId': context_id,
            'auditInfo': {
                'id': str(uuid.uuid4()),
                'contextName': function_name,
                'openTimestamp': self.start_time,
                'props': {
                    'REQUEST': data['event'] if data['request_skipped'] is False else None
                },
                'children': []

            },
            'properties': {
                'request': data['event'] if data['request_skipped'] is False else None,
                'response': None,
                'coldStart': 'true' if TracePlugin.IS_COLD_START else 'false',
                'functionRegion': utils.get_environment_variable(constants.AWS_REGION, ''),
                'functionMemoryLimitInMB': getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None),
                'logGroupName': getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None),
                'logStreamName': getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None),
                'functionARN': getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN),
                'requestId': getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None),
                'timeout': 'false'
            }

        }
        self.scope = self.tracer.start_active_span(operation_name=function_name,
                                                   start_time=self.start_time,
                                                   finish_on_close=True)


        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        self.end_time = int(time.time() * 1000)
        self.scope.close()

        duration = self.end_time - self.start_time

        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['endTimestamp'] = self.end_time
        self.trace_data['properties']['timeout'] = data.get('timeoutString', 'false')

        span_tree = self.tracer.recorder.span_tree if self.tracer is not None else None

        self.trace_data['auditInfo']['closeTimestamp'] = self.end_time
        self.trace_data['auditInfo']['children'] = self.create_children_audtit_info(span_tree)

        if 'error' in data:
            error = data['error']
            error_type = type(error)
            exception = {
                'errorType': error_type.__name__,
                'errorMessage': str(error)
            }
            self.trace_data['errors'] = self.trace_data['errors'] or []
            self.trace_data['errors'].append(error_type.__name__)
            self.trace_data['thrownError'] = error_type.__name__
            errors = []
            if 'errors' in self.trace_data['auditInfo']:
                errors = self.trace_data['auditInfo']['errors']
            self.trace_data['auditInfo']['errors'] = errors
            self.trace_data['auditInfo']['errors'].append(exception)
            self.trace_data['auditInfo']['thrownError'] = exception
            self.trace_data['auditInfo']['closeTimestamp'] = self.end_time

        if 'response' in data:
            self.trace_data['properties']['response'] = data['response']
            self.trace_data['auditInfo']['props']['RESPONSE'] = data['response']


        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'AuditData',
            'dataFormatVersion': constants.DATA_FORMAT_VERSION,
            'data': self.trace_data
        }
        reporter.add_report(report_data)


    def create_children_audtit_info(self, node):
        auditInfos = []
        children = node.children
        for child in children:
            auditInfos.append(self.build_audit_info(child))

        return auditInfos

    def build_audit_info(self, node):
        if node is None:
            return None
        root_audit_info= self.convert_to_audit(node)
        children = node.children
        visited = [node]
        for child in children:
            if child not in visited:
                child_audit_info = self.build_audit_info(child)
                root_audit_info['children'].append(child_audit_info)
        return root_audit_info


    @staticmethod
    def convert_to_audit(node):
        close_time = node.key.start_time + node.key.duration
        thrown_error = None
        errors = None
        if node.key.get_tag('error'):
            thrown_error = {
                'errorMessage': node.key.get_tag('error.message'),
                'errorType': node.key.get_tag('error.kind')
            }
            errors = [thrown_error]

        audit_info = {
            'contextName': node.key.operation_name,
            'id': node.key.span_id,
            'openTimestamp': int(node.key.start_time),
            'closeTimestamp': int(close_time),
            'thrownError': thrown_error,
            'errors': errors,
            'props': node.key.tags,
            'children': []
        }
        if node.key.logs is not None and len(node.key.logs) > 0:
            audit_info['props']['LOGS'] = node.key.logs
        return audit_info
