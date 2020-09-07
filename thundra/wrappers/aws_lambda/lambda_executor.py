import math
import time
import uuid

from thundra import utils, constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.plugins.invocation import invocation_trace_support
from thundra.plugins.log.thundra_logger import debug_logger
from thundra.wrappers.aws_lambda import lambda_event_utils


def start_trace(plugin_context, execution_context, tracer):
    set_start_time(execution_context)
    context = execution_context.platform_data['originalContext']
    # Start root span
    scope = tracer.start_active_span(operation_name=context.function_name,
                                     start_time=execution_context.start_timestamp,
                                     finish_on_close=False,
                                     trace_id=execution_context.trace_id,
                                     transaction_id=execution_context.transaction_id,
                                     execution_context=execution_context)
    root_span = scope.span

    # Set root span class and domain names
    root_span.class_name = constants.ClassNames['LAMBDA']
    root_span.domain_name = constants.DomainNames['API']
    # Add root span tags
    execution_context.span_id = root_span.context.span_id
    root_span.set_tag('aws.region', utils.get_aws_region_from_arn(
        getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)))
    root_span.set_tag('aws.lambda.name', context.function_name)
    root_span.set_tag('aws.lambda.arn', getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
    root_span.set_tag('aws.lambda.memory.limit', getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None))
    root_span.set_tag('aws.lambda.log_group_name', getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None))
    root_span.set_tag('aws.lambda.log_stream_name', getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None))
    root_span.set_tag('aws.lambda.invocation.coldstart', plugin_context.request_count == 1)
    root_span.set_tag('aws.lambda.invocation.timeout', execution_context.timeout)
    root_span.set_tag('aws.lambda.invocation.request_id',
                      getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None))
    inject_trigger_tags(root_span, execution_context.platform_data['originalEvent'], context)

    root_span.on_started()
    execution_context.root_span = root_span
    execution_context.scope = scope


def inject_trigger_tags(span, original_event, original_context):
    try:
        lambda_event_utils.extract_trace_link_from_event(original_event)
        lambda_event_type = lambda_event_utils.get_lambda_event_type(original_event, original_context)

        if lambda_event_type == lambda_event_utils.LambdaEventType.Kinesis:
            lambda_event_utils.inject_trigger_tags_for_kinesis(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.Firehose:
            lambda_event_utils.inject_trigger_tags_for_firehose(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.DynamoDB:
            lambda_event_utils.inject_trigger_tags_for_dynamodb(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.SNS:
            lambda_event_utils.inject_trigger_tags_for_sns(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.SQS:
            lambda_event_utils.inject_trigger_tags_for_sqs(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.S3:
            lambda_event_utils.inject_trigger_tags_for_s3(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudWatchSchedule:
            lambda_event_utils.inject_trigger_tags_for_cloudwatch_schedule(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudWatchLogs:
            lambda_event_utils.inject_trigger_tags_for_cloudwatch_logs(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudFront:
            lambda_event_utils.inject_trigger_tags_for_cloudfront(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.APIGatewayProxy:
            lambda_event_utils.inject_trigger_tags_for_api_gateway_proxy(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.APIGateway:
            lambda_event_utils.inject_trigger_tags_for_api_gateway(span, original_event)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.Lambda:
            lambda_event_utils.inject_trigger_tags_for_lambda(span, original_context)
        elif lambda_event_type == lambda_event_utils.LambdaEventType.EventBridge:
            lambda_event_utils.inject_trigger_tags_for_eventbridge(span, original_event)
    except Exception as e:
        debug_logger("Cannot inject trigger tags. " + str(e))


def finish_trace(execution_context):
    set_end_time(execution_context)
    root_span = execution_context.root_span
    scope = execution_context.scope
    try:
        root_span.finish(f_time=execution_context.finish_timestamp)
    except Exception:
        # TODO: handle root span finish errors
        pass
    finally:
        scope.close()

    trigger_class_name = root_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME'])

    # Disable request data sending for cloudwatchlog, firehose and kinesis if not
    # enabled by configuration because requests can get too big for these
    enable_request_data = True
    if (
            trigger_class_name == constants.ClassNames['CLOUDWATCHLOG'] and
            not ConfigProvider.get(config_names.THUNDRA_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE)) or (

            trigger_class_name == constants.ClassNames['FIREHOSE'] and
            not ConfigProvider.get(config_names.THUNDRA_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE)) or (

            trigger_class_name == constants.ClassNames['KINESIS'] and
            not ConfigProvider.get(config_names.THUNDRA_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE)
    ):
        enable_request_data = False

    # ADDING TAGS #
    if (not ConfigProvider.get(config_names.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP)) and enable_request_data:
        root_span.set_tag('aws.lambda.invocation.request', execution_context.platform_data['originalEvent'])
    if not ConfigProvider.get(config_names.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP):
        root_span.set_tag('aws.lambda.invocation.response', execution_context.response)

    if trigger_class_name == constants.ClassNames['APIGATEWAY']:
        process_api_gw_response(execution_context)


def process_api_gw_response(execution_context):
    try:
        if execution_context.response:
            response = execution_context.response
            if not response.get('headers'):
                response['headers'] = {}
            resource_path = utils.extract_api_gw_resource_name(execution_context.platform_data['originalEvent'])
            if resource_path:
                response['headers'][constants.TRIGGER_RESOURCE_NAME_TAG] = resource_path
    except:
        pass


def set_start_time(execution_context):
    if not execution_context.start_timestamp:
        execution_context.start_timestamp = int(time.time() * 1000)


def set_end_time(execution_context):
    if not execution_context.finish_timestamp:
        execution_context.finish_timestamp = int(time.time() * 1000)


def start_invocation(plugin_context, execution_context):
    set_start_time(execution_context)

    if not execution_context.transaction_id:
        execution_context.transaction_id = str(uuid.uuid4())
    invocation_data = {
        'id': str(uuid.uuid4()),
        'type': "Invocation",
        'agentVersion': constants.THUNDRA_AGENT_VERSION,
        'dataModelVersion': constants.DATA_FORMAT_VERSION,
        'traceId': execution_context.trace_id,
        'transactionId': execution_context.transaction_id,
        'spanId': execution_context.span_id,
        'applicationPlatform': constants.CONTEXT_APPLICATION_PLATFORM,
        'functionRegion': utils.get_env_variable(constants.AWS_REGION, default=''),
        'duration': None,
        'startTimestamp': execution_context.start_timestamp,
        'finishTimestamp': None,
        'erroneous': False,
        'errorType': '',
        'errorMessage': '',
        'errorCode': -1,
        'coldStart': plugin_context.request_count == 1,
        'timeout': False,
        'tags': {},
    }

    # Add application related data
    application_info = plugin_context.application_info
    invocation_data.update(application_info)

    execution_context.invocation_data = invocation_data


def get_response_status(execution_context):
    try:
        status_code = execution_context.response['statusCode']
    except:
        return None
    return status_code


def inject_step_function_info(execution_context, outgoing_trace_links):
    try:
        response = execution_context.response
        event = execution_context.platform_data['originalEvent']
        if ConfigProvider.get(config_names.THUNDRA_LAMBDA_AWS_STEPFUNCTIONS):
            trace_link = str(uuid.uuid4())
            step = 0
            if '_thundra' in event:
                step = event['_thundra']['step']

            if isinstance(response, dict):
                response['_thundra'] = {
                    'trace_link': trace_link,
                    'step': step + 1
                }
            outgoing_trace_links["outgoingTraceLinks"].append(trace_link)
    except Exception as e:
        print(e)


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


def finish_invocation(execution_context):
    set_end_time(execution_context)

    context = execution_context.platform_data['originalContext']
    invocation_data = execution_context.invocation_data

    _, used_mem = utils.process_memory_usage()
    used_mem_in_mb = used_mem / 1048576

    # Add user tags
    invocation_data['userTags'] = execution_context.user_tags

    # Add agent tags
    invocation_data['tags'] = execution_context.tags

    response_status_code = get_response_status(execution_context)

    if response_status_code and not invocation_data['userTags'].get('http.status_code'):
        invocation_data['userTags']['http.status_code'] = response_status_code

    # Get resources
    resources = invocation_trace_support.get_resources()
    invocation_data.update(resources)

    # Get incoming trace links
    incoming_trace_links = invocation_trace_support.get_incoming_trace_links()
    invocation_data.update(incoming_trace_links)

    # Get outgoing trace links
    outgoing_trace_links = invocation_trace_support.get_outgoing_trace_links()

    # Inject trace link to response and add it to outgoing trace links
    inject_step_function_info(execution_context, outgoing_trace_links)

    invocation_data.update(outgoing_trace_links)

    # Check errors
    user_error = execution_context.user_error
    if execution_context.error:
        set_error(invocation_data, execution_context.error)
    elif user_error:
        set_error(invocation_data, user_error)

    invocation_data['timeout'] = execution_context.timeout

    duration = execution_context.finish_timestamp - execution_context.start_timestamp
    invocation_data['duration'] = int(duration)
    invocation_data['finishTimestamp'] = int(execution_context.finish_timestamp)

    arn = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)

    # Add AWS tags
    invocation_data['tags']['aws.region'] = utils.get_aws_region_from_arn(
        getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
    invocation_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
    invocation_data['tags']['aws.lambda.arn'] = arn
    invocation_data['tags']['aws.account_no'] = utils.get_aws_account_no(arn)
    invocation_data['tags']['aws.lambda.memory_limit'] = int(getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, 0))
    invocation_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None)
    invocation_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
    invocation_data['tags']['aws.lambda.invocation.coldstart'] = invocation_data['coldStart']
    invocation_data['tags']['aws.lambda.invocation.timeout'] = execution_context.timeout
    invocation_data['tags']['aws.lambda.invocation.request_id'] = getattr(context, constants.CONTEXT_AWS_REQUEST_ID,
                                                                          None)
    invocation_data['tags']['aws.lambda.invocation.memory_usage'] = math.floor(used_mem_in_mb)

    xray_info = utils.parse_x_ray_trace_info()
    if xray_info.get("trace_id"):
        invocation_data['tags']['aws.xray.trace.id'] = xray_info.get("trace_id")
    if xray_info.get("segment_id"):
        invocation_data['tags']['aws.xray.segment.id'] = xray_info.get("segment_id")

    execution_context.invocation_data = invocation_data
