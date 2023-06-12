import logging
import uuid

from opentracing import Format

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.plugins.invocation import invocation_support, invocation_trace_support
from catchpoint.utils import get_normalized_path
import catchpoint.wrappers.cp_wrapper_utils as cp_wrapper_utils

Logger = logging.getLogger(__name__)

def start_trace(execution_context, tracer, class_name, domain_name, request, request_route_path=None):
    propagated_span_context = tracer.extract(Format.HTTP_HEADERS, request.get('headers'))
    trace_id = str(uuid.uuid4())
    incoming_span_id = None
    if propagated_span_context:
        trace_id = propagated_span_context.trace_id
        incoming_span_id = propagated_span_context.span_id

    # Start root span
    url_path_depth = ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH)
    normalized_path = get_normalized_path(request.get('path'), url_path_depth)
    operation_name = request_route_path or normalized_path
    scope = tracer.start_active_span(operation_name=operation_name,
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
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_REQUEST_SKIP, True):
        root_span.set_tag(constants.HttpTags['BODY'], request.get('body'))
    execution_context.root_span = root_span
    execution_context.scope = scope
    execution_context.trace_id = trace_id

    if request_route_path:
        trigger_operation_name = request.get('host', '') + request_route_path
    else:
        trigger_operation_name = request.get('headers').get(constants.TRIGGER_RESOURCE_NAME_KEY) or \
                             request.get('host', '') + normalized_path
    execution_context.application_resource_name = request_route_path or normalized_path
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [trigger_operation_name])
    execution_context.trigger_operation_name = trigger_operation_name

    invocation_support.set_agent_tag(constants.HttpTags['HTTP_METHOD'], request.get('method'))
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'API')
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'HTTP')

    if incoming_span_id:
        invocation_trace_support.add_incoming_trace_link(incoming_span_id)


def update_application_info(application_info_provider, application_info, app_class_name):
    application_info_provider.update({
        'applicationName': application_info.get('applicationName', 'catchpoint-app'),
        'applicationClassName': app_class_name,
        'applicationDomainName': 'API',
        'applicationInstanceId': application_info.get('applicationInstanceId',
                                                      str(uuid.uuid4())),
        'applicationId': 'python:{}:{}:{}'.format(app_class_name,
                                                  application_info.get('applicationRegion', ''),
                                                  application_info.get('applicationName',
                                                                       'catchpoint-app'))
    })


def process_request_route(execution_context, request_route_path, request_host):
    if request_route_path and execution_context and execution_context.scope:
        trigger_operation_name = request_host + request_route_path
        execution_context.scope.span.operation_name = request_route_path
        execution_context.trigger_operation_name = trigger_operation_name
        execution_context.application_resource_name = request_route_path
        invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [trigger_operation_name])


def finish_trace(execution_context):
    root_span = execution_context.root_span
    scope = execution_context.scope
    try:
        root_span.finish(f_time=execution_context.finish_timestamp)
        cp_wrapper_utils.on_finish(execution_context, execution_context.platform_data["request"],
                                   execution_context.response, root_span)
    except Exception:
        # TODO: handle root span finish errors
        pass
    finally:
        try:
            scope.close()
        except Exception as e:
            Logger.debug("Error occured while closing scope: {}".format(e))
            pass
