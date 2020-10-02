import uuid

from thundra import constants
from thundra.wrappers import wrapper_utils, web_wrapper_utils


def start_trace(plugin_context, execution_context, tracer):
    request = execution_context.platform_data['request']

    request = {
        'method': request.method,
        'host': request.get_host().split(':')[0],
        'query_params': request.GET,
        'body': request.body,
        'headers': request.headers,
        'path': request.path
    }
    web_wrapper_utils.start_trace(execution_context, tracer, 'Django', 'API', request)


def finish_trace(execution_context):
    root_span = execution_context.root_span
    if execution_context.response:
        root_span.set_tag(constants.HttpTags['HTTP_STATUS'], execution_context.response.status_code)
        root_span.set_tag('response_body', execution_context.response.content)
        if execution_context.trigger_operation_name:
            execution_context.response[constants.TRIGGER_RESOURCE_NAME_TAG] = execution_context.trigger_operation_name
    scope = execution_context.scope
    try:
        root_span.finish(f_time=execution_context.finish_timestamp)
    except Exception:
        # TODO: handle root span finish errors
        pass
    finally:
        scope.close()


def start_invocation(plugin_context, execution_context):
    if not execution_context.transaction_id:
        execution_context.transaction_id = str(uuid.uuid4())

    execution_context.invocation_data = wrapper_utils.create_invocation_data(plugin_context, execution_context)


def finish_invocation(execution_context):
    wrapper_utils.finish_invocation(execution_context)
