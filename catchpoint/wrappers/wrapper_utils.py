import time
import uuid

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.context.execution_context import ExecutionContext
from catchpoint.plugins.invocation import invocation_trace_support
from catchpoint.plugins.invocation.invocation_plugin import InvocationPlugin
from catchpoint.plugins.log.log_plugin import LogPlugin
from catchpoint.plugins.metric.metric_plugin import MetricPlugin
from catchpoint.plugins.trace.trace_plugin import TracePlugin


def initialize_plugins(plugin_context, disable_trace, disable_metric, disable_log, config):
    plugins = []
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_DISABLE, disable_trace):
        plugins.append(TracePlugin(plugin_context=plugin_context, config=config.trace_config))
    plugins.append(InvocationPlugin(plugin_context=plugin_context))

    if not ConfigProvider.get(config_names.CATCHPOINT_METRIC_DISABLE, disable_metric):
        plugins.append(MetricPlugin(plugin_context=plugin_context, config=config.metric_config))

    if not ConfigProvider.get(config_names.CATCHPOINT_LOG_DISABLE, disable_log):
        plugins.append(LogPlugin(plugin_context=plugin_context, config=config.log_config))
    return plugins


def create_invocation_data(plugin_context, execution_context):
    if not execution_context.transaction_id:
        execution_context.transaction_id = str(uuid.uuid4())
    invocation_data = {
        'id': str(uuid.uuid4()),
        'type': "Invocation",
        'agentVersion': constants.CATCHPOINT_AGENT_VERSION,
        'dataModelVersion': constants.DATA_FORMAT_VERSION,
        'traceId': execution_context.trace_id,
        'transactionId': execution_context.transaction_id,
        'spanId': execution_context.span_id,
        'applicationPlatform': '',
        'applicationRegion': plugin_context.application_info.get('applicationRegion'),
        'duration': None,
        'startTimestamp': execution_context.start_timestamp,
        'finishTimestamp': None,
        'erroneous': False,
        'errorType': '',
        'errorMessage': '',
        'errorStack': '',
        'errorCode': -1,
        'coldStart': plugin_context.request_count == 1,
        'timeout': False,
        'tags': {},
    }

    # Add application related data
    application_info = plugin_context.application_info
    invocation_data.update(application_info)

    return invocation_data


def finish_invocation(execution_context):
    invocation_data = execution_context.invocation_data

    # Add user tags
    invocation_data['userTags'] = execution_context.user_tags

    # Add agent tags
    invocation_data['tags'].update(execution_context.tags)

    # Get resources
    resources = invocation_trace_support.get_resources()
    invocation_data.update(resources)

    # Get incoming trace links
    incoming_trace_links = invocation_trace_support.get_incoming_trace_links()
    invocation_data.update(incoming_trace_links)

    # Get outgoing trace links
    outgoing_trace_links = invocation_trace_support.get_outgoing_trace_links()
    invocation_data.update(outgoing_trace_links)

    # Check errors
    user_error = execution_context.user_error
    if execution_context.error:
        set_error(invocation_data, execution_context.error)
    elif user_error:
        set_error(invocation_data, user_error)

    duration = execution_context.finish_timestamp - execution_context.start_timestamp
    invocation_data['duration'] = int(duration)
    invocation_data['finishTimestamp'] = int(execution_context.finish_timestamp)
    invocation_data['timeout'] = execution_context.timeout
    invocation_data['applicationResourceName'] = execution_context.application_resource_name

    execution_context.invocation_data = invocation_data


def set_error(invocation_data, error):
    invocation_data['erroneous'] = True
    if isinstance(error, Exception):
        error_type = type(error)
        invocation_data['errorType'] = error_type.__name__
        invocation_data['errorMessage'] = str(error)
        if hasattr(error, 'code'):
            invocation_data['errorCode'] = error.code
    elif isinstance(error, dict):
        invocation_data['errorType'] = error.get('type')
        invocation_data['errorMessage'] = error.get('message')
        invocation_data['errorStack'] = error.get('traceback', None)


def create_execution_context():
    transaction_id = str(uuid.uuid4())
    start_timestamp = int(time.time() * 1000)
    return ExecutionContext(transaction_id=transaction_id, start_timestamp=start_timestamp)


def set_response_status(execution_context, response_status_code):
    if response_status_code:
        if execution_context.invocation_data.get('userTags') is None:
            execution_context.invocation_data['userTags'] = {}
        if execution_context.invocation_data['userTags'].get('http.status_code') is None:
            execution_context.invocation_data['userTags']['http.status_code'] = response_status_code
