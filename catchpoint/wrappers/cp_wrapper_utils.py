import uuid
import json
import logging

from catchpoint import constants, utils
from catchpoint.application.application_info_provider import ApplicationInfoProvider
from catchpoint.encoder import to_json
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
import catchpoint.wrappers.wrapper_utils as wrapper_utils

logger = logging.getLogger(__name__)


def on_finish(execution_context, request, response, span):
    try:
        if is_triggered_from_catchpoint(request):
            on_catchpoint_request_finish(execution_context, request, response, span)
    except Exception as e:
        logger.error('ERROR: {}'.format(e))


def is_triggered_from_catchpoint(request):
    if request and request.headers:
        headers = request.headers
        user_agent = headers.get(constants.HTTPHeaders['USER_AGENT'])
        if user_agent is None:
            user_agent = headers.get(constants.HTTPHeaders['USER_AGENT'].lower())
        return 'catchpoint' in user_agent.lower() if user_agent else False
    return False


def on_catchpoint_request_finish(execution_context, request, response, span):
    api_key = ConfigProvider.get(config_names.CATCHPOINT_APIKEY, None)
    headers = request.headers if request and request.headers else {}
    region_name = headers.get(constants.CatchpointHeaders.get('REGION_NAME'))
    country_name = headers.get(constants.CatchpointHeaders.get('COUNTRY_NAME'))
    city_name = headers.get(constants.CatchpointHeaders.get('CITY_NAME'))
    test_id = headers.get(constants.CatchpointHeaders.get('TEST_ID'))
    application_name = generate_catchpoint_application_name(region_name, country_name, city_name)
    application_region = region_name if region_name else ''
    trace_id = span.context.trace_id
    transaction_id = utils.generate_id()
    span_id = utils.generate_id()
    start_timestamp = span.start_time
    finish_timestamp = span.finish_time
    duration = finish_timestamp - start_timestamp
    application_info = get_catchpoint_application_info(application_name, application_region)

    # create catchpoint invocation data
    resource = get_catchpoint_request_resource(execution_context, request, span, duration)
    invocation_data = create_catchpoint_request_invocation(execution_context, application_info, region_name,
                                                           country_name, city_name, test_id, trace_id, transaction_id,
                                                           span_id, start_timestamp, finish_timestamp, resource)
    execution_context.report(create_report_data(api_key, 'Invocation', invocation_data))

    # create catchpoint span data
    span_data = create_catchpoint_request_span(application_info, span, resource, region_name, country_name, city_name, 
                                               test_id, trace_id, transaction_id, span_id, start_timestamp, finish_timestamp)
    execution_context.report(create_report_data(api_key, 'Span', span_data))

    if response and hasattr(response, 'headers'):
        if response.headers is None:
            response.headers = {}
        response.headers[constants.CATCHPOINT_TRACE_ID_KEY] = span.context.trace_id


def create_catchpoint_request_invocation(execution_context, application_info, region_name, country_name, city_name,
                                         test_id, trace_id, transaction_id, span_id, start_timestamp, finish_timestamp,
                                         resource):
    if not execution_context.transaction_id:
        execution_context.transaction_id = str(uuid.uuid4())
    invocation_data = {
        'id': str(uuid.uuid4()),
        'type': 'Invocation',
        'agentVersion': constants.CatchpointProperties.get('AGENT_VERSION'),
        'dataModelVersion': constants.DATA_FORMAT_VERSION,
        'traceId': trace_id,
        'transactionId': transaction_id,
        'spanId': span_id,
        'applicationPlatform': '',
        'applicationRegion': region_name if region_name else '',
        'duration': finish_timestamp - start_timestamp,
        'startTimestamp': start_timestamp,
        'finishTimestamp': finish_timestamp,
        'coldStart': False,
        'timeout': False,
        'erroneous': False,
        'errorType': '',
        'errorCode': -1,
        'errorMessage': '',
        'errorStack': None,
        'tags': {
            constants.CatchpointTags.get('REGION_NAME'): region_name,
            constants.CatchpointTags.get('COUNTRY_NAME'): country_name,
            constants.CatchpointTags.get('CITY_NAME'): city_name,
            constants.CatchpointTags.get('TEST_ID'): test_id
        },
        'resources': [resource],
        'userTags': {},
        'incomingTraceLinks': [],
        'outgoingTraceLinks': []
    }

    inject_application_info(invocation_data, application_info)
    if execution_context.error:
        wrapper_utils.set_error(invocation_data, execution_context.error)
    return invocation_data


def create_catchpoint_request_span(application_info, root_span, resource, region_name, country_name,
                                   city_name, test_id, trace_id, transaction_id, span_id, start_timestamp,
                                   finish_timestamp):
        span_data = {
            'id': span_id,
            'type': 'Span',
            'agentVersion': constants.CatchpointProperties.get('AGENT_VERSION'),
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'domainName': constants.CatchpointProperties.get('HTTP_REQUEST_DOMAIN_NAME'),
            'className': constants.CatchpointProperties.get('HTTP_REQUEST_CLASS_NAME'),
            'serviceName': application_info.get('applicationName'),
            'traceId': trace_id,
            'transactionId': transaction_id,
            'spanOrder': 0,
            'operationName': resource.get('resourceName'),
            'duration': finish_timestamp - start_timestamp,
            'startTimestamp': start_timestamp,
            'finishTimestamp': finish_timestamp,
            'tags': {
                constants.HttpTags.get('HTTP_URL'): root_span.get_tag(constants.HttpTags.get('HTTP_URL')),
                constants.HttpTags.get('HTTP_HOST'): root_span.get_tag(constants.HttpTags.get('HTTP_HOST')),
                constants.HttpTags.get('HTTP_PATH'): root_span.get_tag(constants.HttpTags.get('HTTP_PATH')),
                constants.HttpTags.get('HTTP_METHOD'): root_span.get_tag(constants.HttpTags.get('HTTP_METHOD')),
                constants.HttpTags.get('QUERY_PARAMS'): root_span.get_tag(constants.HttpTags.get('QUERY_PARAMS')),
                constants.HttpTags.get('HTTP_STATUS'): root_span.get_tag(constants.HttpTags.get('HTTP_STATUS')),
                constants.CatchpointTags.get('REGION_NAME'): region_name,
                constants.CatchpointTags.get('COUNTRY_NAME'): country_name,
                constants.CatchpointTags.get('CITY_NAME'): city_name,
                constants.CatchpointTags.get('TEST_ID'): test_id
            }
        }
        inject_application_info(span_data, application_info)
        return span_data


def inject_application_info(data, application_info):
    data.update(application_info)
    data['applicationRuntime'] = ""
    data['applicationRuntimeVersion'] = ""


def get_catchpoint_application_info(application_name, application_region):
    application_id = constants.CatchpointProperties.get('APP_ID_TEMPLATE')
    application_id = application_id.replace(constants.CatchpointProperties.get('APP_NAME_PLACEHOLDER'),
                                                application_name)
    application_id = application_id.replace(constants.CatchpointProperties.get('APP_REGION_PLACEHOLDER'),
                                                application_region)
    return {
        'applicationId': application_id,
        'applicationInstanceId': utils.generate_id_from(application_id),
        'applicationName': application_name,
        'applicationClassName': constants.CatchpointProperties.get('APP_CLASS_NAME'),
        'applicationDomainName': constants.CatchpointProperties.get('APP_DOMAIN_NAME'),
        'applicationRegion': application_region,
        'applicationVersion': '',
        'applicationRuntime': None,
        'applicationRuntimeVersion': None,
        'applicationStage': '',
        'applicationTags': {},
    }


def get_catchpoint_request_resource(execution_context, request, span, duration):
    operation_name = execution_context.trigger_operation_name
    if operation_name is None:
        operation_name = span.operation_name
    error_type = get_error_type(execution_context.error)
    resource_errors = [error_type] if error_type else None
    return {
        'resourceType': constants.CatchpointProperties.get('HTTP_REQUEST_CLASS_NAME'),
        'resourceName': operation_name,
        'resourceOperation': request.method,
        'resourceCount': 1,
        'resourceErrorCount': 1 if execution_context.error else 0,
        'resourceErrors': resource_errors,
        'resourceDuration': duration,
        'resourceMaxDuration': duration,
        'resourceAvgDuration': duration
    }


def get_error_type(error):
    try:
        if isinstance(error, Exception):
            error_type = type(error)
            return error_type.__name__
        elif isinstance(error, dict):
            return error.get('type')
        return None
    except Exception:
        return None


def generate_catchpoint_application_name(region_name, country_name, city_name):
    if city_name:
        return city_name
    elif country_name:
        return country_name
    elif region_name:
        return region_name
    else:
        return constants.CatchpointProperties.get('DEFAULT_APP_NAME')


def create_report_data(api_key, data_type, data):
    report_data = {
        'apiKey': api_key,
        'type': data_type,
        'dataModelVersion': constants.DATA_FORMAT_VERSION,
        'data': data
    }
    return json.loads(to_json(report_data))
