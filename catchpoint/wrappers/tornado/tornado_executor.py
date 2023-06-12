from catchpoint import constants
from catchpoint.wrappers import wrapper_utils, web_wrapper_utils


def start_trace(plugin_context, execution_context, tracer):
    request = execution_context.platform_data['request']
    request_route_path = str(request.path) if request.path else None

    _request = {
        'method': request.method,
        'host': request.host.split(':')[0],
        'query_params': request.query,
        'body': request.body,
        'headers': request.headers,
        'path': request.path
    }

    web_wrapper_utils.start_trace(execution_context, tracer, 'Tornado', 'API', _request, request_route_path)


def finish_trace(execution_context):
    root_span = execution_context.root_span
    if execution_context.response:
        status_code = get_response_status(execution_context)
        if status_code:
            root_span.set_tag(constants.HttpTags['HTTP_STATUS'], status_code)
        if execution_context.trigger_operation_name and execution_context.response and hasattr(
                execution_context.response, 'headers'):
            execution_context.response.headers[
                constants.TRIGGER_RESOURCE_NAME_KEY] = execution_context.trigger_operation_name
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
