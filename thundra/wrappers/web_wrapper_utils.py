import uuid

from opentracing import Format

from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.plugins.invocation import invocation_support, invocation_trace_support
from thundra.utils import get_normalized_path


def start_trace(execution_context, tracer, class_name, domain_name, request):
    propagated_span_context = tracer.extract(Format.HTTP_HEADERS, request.get('headers'))
    trace_id = str(uuid.uuid4())
    incoming_span_id = None
    if propagated_span_context:
        trace_id = propagated_span_context.trace_id
        incoming_span_id = propagated_span_context.span_id

    # Start root span
    url_path_depth = ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_URL_DEPTH)
    normalized_path = get_normalized_path(request.get('path'), url_path_depth)
    scope = tracer.start_active_span(operation_name=normalized_path,
                                     child_of=propagated_span_context,
                                     start_time=execution_context.start_timestamp,
                                     finish_on_close=False,
                                     trace_id=trace_id,
                                     transaction_id=execution_context.transaction_id,
                                     execution_context=execution_context)
    root_span = scope.span

    # Set root span class and domain names
    root_span.class_name = class_name
    root_span.domain_name = domain_name

    # Add root span tags
    execution_context.span_id = root_span.context.span_id
    root_span.on_started()
    root_span.set_tag(constants.HttpTags['HTTP_METHOD'], request.get('method'))
    root_span.set_tag(constants.HttpTags['HTTP_HOST'], request.get('host', ''))
    root_span.set_tag(constants.HttpTags['QUERY_PARAMS'], request.get('query_params'))
    root_span.set_tag(constants.HttpTags['HTTP_PATH'], request.get('path'))
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_REQUEST_SKIP):
        root_span.set_tag(constants.HttpTags['BODY'], request.get('body'))
    execution_context.root_span = root_span
    execution_context.scope = scope
    execution_context.trace_id = trace_id

    trigger_operation_name = request.get('headers').get(constants.TRIGGER_RESOURCE_NAME_TAG) or \
                             request.get('host', '') + normalized_path
    execution_context.application_resource_name = normalized_path
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [trigger_operation_name])
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'API')
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'HTTP')

    if incoming_span_id:
        invocation_trace_support.add_incoming_trace_link(incoming_span_id)


def update_application_info(application_info_provider, application_info, app_class_name):
    application_info_provider.update({
        'applicationName': application_info.get('applicationName', 'thundra-app'),
        'applicationClassName': app_class_name,
        'applicationDomainName': 'API',
        'applicationInstanceId': application_info.get('applicationInstanceId',
                                                      str(uuid.uuid4())),
        'applicationId': 'python:{}:{}:{}'.format(app_class_name,
                                                  application_info.get('applicationRegion', ''),
                                                  application_info.get('applicationName',
                                                                       'thundra-app'))
    })


def finish_trace(execution_context):
    root_span = execution_context.root_span
    if execution_context.response:
        root_span.set_tag(constants.HttpTags['HTTP_STATUS'], execution_context.response.status_code)
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
