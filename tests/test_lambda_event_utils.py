from __future__ import unicode_literals

import base64
import hashlib

import mock
import pytest
import simplejson as json

from catchpoint.compat import str
from catchpoint.context.execution_context_manager import ExecutionContextManager

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

from catchpoint import constants
from catchpoint.wrappers.aws_lambda import lambda_event_utils
from catchpoint.opentracing.tracer import CatchpointTracer
from catchpoint.plugins import invocation

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from gzip import GzipFile


@pytest.fixture
def tracer_and_invocation_support():
    with ExitStack() as stack:
        # Just a fancy way of using contexts to avoid an ugly multi-line with statement
        stack.enter_context(mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder.clear'))
        tracer = CatchpointTracer.get_instance()
        invocation_support = invocation.invocation_support
        invocation_trace_support = invocation.invocation_trace_support
        yield tracer, invocation_support, invocation_trace_support


def test_dynamodb_trigger(tracer_and_invocation_support, handler, mock_dynamodb_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    handler(mock_dynamodb_event, mock_context)

    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]
    assert lambda_event_utils.get_lambda_event_type(mock_dynamodb_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.DynamoDB

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames[
        'DYNAMODB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    md5_key = hashlib.md5("Id={N: 101}".encode()).hexdigest()
    md5_image_1 = hashlib.md5("Id={N: 101}, Message={S: New item!}".encode()).hexdigest()
    md5_image_2 = hashlib.md5("Id={N: 101}, Message={S: This item has changed}".encode()).hexdigest()
    region = 'eu-west-2'
    table_name = 'ExampleTableWithStream'
    timestamp = 1480642019

    links = [
        region + ':' + table_name + ':' + str(timestamp) + ':' + 'SAVE' + ':' + md5_key,
        region + ':' + table_name + ':' + str(timestamp + 1) + ':' + 'SAVE' + ':' + md5_key,
        region + ':' + table_name + ':' + str(timestamp + 2) + ':' + 'SAVE' + ':' + md5_key,
        region + ':' + table_name + ':' + str(timestamp) + ':' + 'SAVE' + ':' + md5_image_1,
        region + ':' + table_name + ':' + str(timestamp + 1) + ':' + 'SAVE' + ':' + md5_image_1,
        region + ':' + table_name + ':' + str(timestamp + 2) + ':' + 'SAVE' + ':' + md5_image_1,
        region + ':' + table_name + ':' + str(timestamp) + ':' + 'SAVE' + ':' + md5_image_2,
        region + ':' + table_name + ':' + str(timestamp + 1) + ':' + 'SAVE' + ':' + md5_image_2,
        region + ':' + table_name + ':' + str(timestamp + 2) + ':' + 'SAVE' + ':' + md5_image_2
    ]

    assert sorted(invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks')) == sorted(links)


def test_dynamodb_trigger_delete_event(tracer_and_invocation_support, handler, mock_dynamodb_delete_event,
                                       mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    handler(mock_dynamodb_delete_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]
    assert lambda_event_utils.get_lambda_event_type(mock_dynamodb_delete_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.DynamoDB

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames[
        'DYNAMODB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    md5_key = hashlib.md5("Id={N: 101}".encode()).hexdigest()
    region = 'eu-west-2'
    table_name = 'ExampleTableWithStream'
    timestamp = 1480642019

    links = [
        region + ':' + table_name + ':' + str(timestamp) + ':' + 'DELETE' + ':' + md5_key,
        region + ':' + table_name + ':' + str(timestamp + 1) + ':' + 'DELETE' + ':' + md5_key,
        region + ':' + table_name + ':' + str(timestamp + 2) + ':' + 'DELETE' + ':' + md5_key
    ]
    assert sorted(invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks')) == sorted(links)


def test_dynamodb_trigger_trace_injected(tracer_and_invocation_support, handler, mock_dynamodb_event_trace_injected,
                                         mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    handler(mock_dynamodb_event_trace_injected, mock_context)

    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_dynamodb_event_trace_injected,
                                                    mock_context) == lambda_event_utils.LambdaEventType.DynamoDB

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames[
        'DYNAMODB']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    assert sorted(invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks')) == sorted(
        ['SAVE:test_id1', 'SAVE:test_id2', 'DELETE:test_id3'])


def test_sqs_trigger(tracer_and_invocation_support, handler, mock_sqs_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support

    handler(mock_sqs_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_sqs_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.SQS

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'MESSAGING']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']

    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == [
        "19dd0b57-b21e-4ac1-bd88-01bbb068cb78"]


def test_sns_trigger(tracer_and_invocation_support, handler, mock_sns_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    handler(mock_sns_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]
    assert lambda_event_utils.get_lambda_event_type(mock_sns_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.SNS

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'MESSAGING']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']

    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == [
        "95df01b4-ee98-5cb9-9903-4c221d41eb5e"]


def test_kinesis_trigger(tracer_and_invocation_support, handler, mock_kinesis_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support

    handler(mock_kinesis_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_kinesis_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.Kinesis

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'STREAM']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']

    links = ["eu-west-2:example_stream:shardId-000000000000:49545115243490985018280067714973144582180062593244200961"]
    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == links


def test_cloudwatch_schedule_trigger(tracer_and_invocation_support, handler, mock_cloudwatch_schedule_event,
                                     mock_context):
    _, handler = handler
    tracer, invocation_support, _ = tracer_and_invocation_support
    handler(mock_cloudwatch_schedule_event, mock_context)

    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]
    event_type = lambda_event_utils.get_lambda_event_type(mock_cloudwatch_schedule_event,
                                                          mock_context)
    assert event_type == lambda_event_utils.LambdaEventType.CloudWatchSchedule

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']


def test_cloudwatch_logs_trigger(tracer_and_invocation_support, handler, mock_cloudwatch_logs_event, mock_context):
    _, handler = handler
    tracer, invocation_support, _ = tracer_and_invocation_support
    handler(mock_cloudwatch_logs_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_cloudwatch_logs_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.CloudWatchLogs

    compressed_data = base64.b64decode(mock_cloudwatch_logs_event['awslogs']['data'])
    decompressed_data = json.loads(str(GzipFile(fileobj=BytesIO(compressed_data)).read(), 'utf-8'))

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [decompressed_data['logGroup']]

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        decompressed_data['logGroup']]


def test_cloudfront_event_trigger(tracer_and_invocation_support, handler, mock_cloudfront_event, mock_context):
    _, handler = handler
    tracer, invocation_support, _ = tracer_and_invocation_support
    handler(mock_cloudfront_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_cloudfront_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.CloudFront

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']


def test_firehose_trigger(tracer_and_invocation_support, handler, mock_firehose_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_firehose_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.Firehose
    handler(mock_firehose_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['FIREHOSE']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'STREAM']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames[
        'FIREHOSE']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']

    links = [
        "eu-west-2:exampleStream:1495072948:75c5afa1146857f64e92e6bb6e561ded",
        "eu-west-2:exampleStream:1495072949:75c5afa1146857f64e92e6bb6e561ded",
        "eu-west-2:exampleStream:1495072950:75c5afa1146857f64e92e6bb6e561ded",
    ]
    assert sorted(invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks')) == sorted(links)


def test_apigateway_proxy_trigger(tracer_and_invocation_support, handler, mock_apigateway_proxy_event, mock_context):
    _, handler = handler
    tracer, invocation_support, _ = tracer_and_invocation_support
    handler(mock_apigateway_proxy_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_apigateway_proxy_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.APIGatewayProxy

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/{proxy+}']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/{proxy+}']


def test_apigateway_trigger(tracer_and_invocation_support, handler, mock_apigateway_event, mock_context):
    _, handler = handler
    tracer, invocation_support, _ = tracer_and_invocation_support
    handler(mock_apigateway_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_apigateway_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.APIGateway

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        'random.execute-api.us-west-2.amazonaws.com/dev{}']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        'random.execute-api.us-west-2.amazonaws.com/dev{}']


def test_s3_trigger(tracer_and_invocation_support, handler, mock_s3_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_s3_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.S3
    handler(mock_s3_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STORAGE']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'STORAGE']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']

    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == ["EXAMPLE123456789"]


def test_lambda_trigger(tracer_and_invocation_support, handler, mock_event, mock_lambda_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_event,
                                                    mock_lambda_context) == lambda_event_utils.LambdaEventType.Lambda
    handler(mock_event, mock_lambda_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['Sample Context']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['Sample Context']

    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == ["aws_request_id"]


def test_eventbridge_trigger(tracer_and_invocation_support, handler, mock_eventbridge_event, mock_context):
    _, handler = handler
    tracer, invocation_support, invocation_trace_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_eventbridge_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.EventBridge
    handler(mock_eventbridge_event, mock_context)
    execution_context = ExecutionContextManager.get()
    span = execution_context.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['EVENTBRIDGE']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['EC2 Command Status-change Notification']

    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames[
        'MESSAGING']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames[
        'EVENTBRIDGE']
    assert invocation_support.get_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        'EC2 Command Status-change Notification']

    assert invocation_trace_support.get_incoming_trace_links().get('incomingTraceLinks') == [
        "51c0891d-0e34-45b1-83d6-95db273d1602"]
