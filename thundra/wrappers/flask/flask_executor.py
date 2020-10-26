from thundra import constants
from thundra.plugins.invocation import invocation_support

from thundra.wrappers import wrapper_utils, web_wrapper_utils


def start_trace(plugin_context, execution_context, tracer):
    request = execution_context.platform_data['request']

    _request = {
        'method': request.method,
        'host': request.host.split(':')[0],
        'query_params': request.query_string,
        'body': request.data,
        'headers': request.headers,
        'path': request.path
    }

    web_wrapper_utils.start_trace(execution_context, tracer, 'Flask', 'API', _request)

    try:
        if execution_context.scope:
            execution_context.scope.span.operation_name = str(request.url_rule)
            execution_context.trigger_operation_name = str(request.url_rule)
            execution_context.application_resource_name = str(request.url_rule)
            invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'],
                                             [str(request.url_rule)])
    except:
        pass


def finish_trace(execution_context):
    root_span = execution_context.root_span
    if execution_context.response:
        status_code = get_response_status(execution_context)
        if status_code:
            root_span.set_tag(constants.HttpTags['HTTP_STATUS'], status_code)
        if execution_context.trigger_operation_name and execution_context.response and hasattr(
                execution_context.response, 'headers'):
            execution_context.response.headers[
                constants.TRIGGER_RESOURCE_NAME_TAG] = execution_context.trigger_operation_name
    web_wrapper_utils.finish_trace(execution_context)


def start_invocation(plugin_context, execution_context):
    execution_context.invocation_data = wrapper_utils.create_invocation_data(plugin_context, execution_context)


def finish_invocation(execution_context):
    wrapper_utils.finish_invocation(execution_context)

    # Set response status code
    wrapper_utils.set_response_status(execution_context, get_response_status(execution_context))


def get_response_status(execution_context):
    try:
        status_code = execution_context.response.status_code
    except:
        return None
    return status_code
