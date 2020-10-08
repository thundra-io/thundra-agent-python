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
    web_wrapper_utils.finish_trace(execution_context)


def start_invocation(plugin_context, execution_context):
    execution_context.invocation_data = wrapper_utils.create_invocation_data(plugin_context, execution_context)


def finish_invocation(execution_context):
    wrapper_utils.finish_invocation(execution_context)
