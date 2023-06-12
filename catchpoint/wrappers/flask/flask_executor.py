from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider

from catchpoint.wrappers import wrapper_utils, web_wrapper_utils
import logging

Logger = logging.getLogger(__name__)


def start_trace(plugin_context, execution_context, tracer):
    request = execution_context.platform_data['request']
    request_route_path = str(request.url_rule) if request.url_rule else None
    '''
        request data read as stream. This function cache the read data and serve from cache.
        According to function comment in Flask, content length should be checked before read!!! 
    '''
    _request = {
        'method': request.method,
        'host': request.host.split(':')[0],
        'query_params': request.query_string,
        'headers': request.headers,
        'body': None,
        'path': request.path
    }

    web_wrapper_utils.start_trace(execution_context, tracer, 'Flask', 'API', _request, request_route_path)


def finish_trace(execution_context):
    root_span = execution_context.root_span
    """
        Getting request data into start trace occurs unexpected bugs into application process.
        After whole process finish for request data into appşication flow, getting request data and
        set the request_body for root_span as tag.
    """
    try:
        _request = execution_context.platform_data['request']
        req_data = None
        if _request and not ConfigProvider.get(config_names.CATCHPOINT_TRACE_REQUEST_SKIP, False):
            cl = _request.content_length
            if cl == None or cl <= constants.CATCHPOINT_MAX_STREAM_REQUEST_BODY:
                req_data = _request.get_data()
            else:
                req_data = None
            root_span.set_tag(constants.HttpTags['BODY'], req_data)
    except Exception as e:
        Logger.error("Error occured whilst setting request body to root span tag: {}".format(e))
        pass
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
