import mock
import base64
import gzip
import json
import pytest
from contextlib import ExitStack
from thundra import lambda_event_utils, constants
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins import invocation

@pytest.fixture
def tracer_and_invocation_support():
    with ExitStack() as stack:
        # Just a fancy way of using contexts to avoid an ugly multi-line with statement
        stack.enter_context(mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'))
        stack.enter_context(mock.patch('thundra.plugins.invocation.invocation_support.clear'))
        tracer = ThundraTracer.get_instance()
        invocation_support = invocation.invocation_support
        yield tracer, invocation_support

    tracer.clear()
    invocation_support.clear()


def test_dynamodb_trigger(tracer_and_invocation_support, handler, mock_dynamodb_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_dynamodb_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]
    invocation_tags = invocation_support.get_tags()

    assert lambda_event_utils.get_lambda_event_type(mock_dynamodb_event, mock_context) == lambda_event_utils.LambdaEventType.DynamoDB

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']


def test_sqs_trigger(tracer_and_invocation_support, handler, mock_sqs_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_sqs_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_sqs_event, mock_context) == lambda_event_utils.LambdaEventType.SQS

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']

    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']


def test_sns_trigger(tracer_and_invocation_support, handler, mock_sns_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_sns_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_sns_event, mock_context) == lambda_event_utils.LambdaEventType.SNS

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']



def test_kinesis_trigger(tracer_and_invocation_support, handler, mock_kinesis_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_kinesis_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_kinesis_event, mock_context) == lambda_event_utils.LambdaEventType.Kinesis
    
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']


def test_cloudwatch_schedule_trigger(tracer_and_invocation_support, handler, mock_cloudwatch_schedule_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_cloudwatch_schedule_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_cloudwatch_schedule_event,
                mock_context) == lambda_event_utils.LambdaEventType.CloudWatchSchedule
    
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']



def test_cloudwatch_logs_trigger(tracer_and_invocation_support, handler, mock_cloudwatch_logs_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_cloudwatch_logs_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_cloudwatch_logs_event,
                                mock_context) == lambda_event_utils.LambdaEventType.CloudWatchLogs

    compressed_data = base64.b64decode(mock_cloudwatch_logs_event['awslogs']['data'])
    decompressed_data = json.loads(str(gzip.decompress(compressed_data), 'utf-8'))
    
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [decompressed_data['logGroup']]
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [decompressed_data['logGroup']]



def test_cloudfront_event_trigger(tracer_and_invocation_support, handler, mock_cloudfront_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_cloudfront_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_cloudfront_event, mock_context) == lambda_event_utils.LambdaEventType.CloudFront
    
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']



def test_firehose_trigger(tracer_and_invocation_support, handler, mock_firehose_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_firehose_event, mock_context) == lambda_event_utils.LambdaEventType.Firehose
    try:
        response = handler(mock_firehose_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['FIREHOSE']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['FIREHOSE']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']



def test_apigateway_proxy_trigger(tracer_and_invocation_support, handler, mock_apigateway_proxy_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_apigateway_proxy_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_apigateway_proxy_event,
                mock_context) == lambda_event_utils.LambdaEventType.APIGatewayProxy
    
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        '1234567890.execute-api.eu-west-2.amazonaws.com/prod/path/to/resource']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        '1234567890.execute-api.eu-west-2.amazonaws.com/prod/path/to/resource']
    


def test_apigateway_trigger(tracer_and_invocation_support, handler, mock_apigateway_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    try:
        response = handler(mock_apigateway_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert lambda_event_utils.get_lambda_event_type(mock_apigateway_event,
                mock_context) == lambda_event_utils.LambdaEventType.APIGateway

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        'random.execute-api.us-west-2.amazonaws.com/dev{}']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
        'random.execute-api.us-west-2.amazonaws.com/dev{}']


def test_s3_trigger(tracer_and_invocation_support, handler, mock_s3_event, mock_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_s3_event, mock_context) == lambda_event_utils.LambdaEventType.S3
    try:
        response = handler(mock_s3_event, mock_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STORAGE']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']
    
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STORAGE']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']



def test_lambda_trigger(tracer_and_invocation_support, handler, mock_event, mock_lambda_context):
    thundra, handler = handler
    tracer, invocation_support = tracer_and_invocation_support
    assert lambda_event_utils.get_lambda_event_type(mock_event, mock_lambda_context) == lambda_event_utils.LambdaEventType.Lambda
    try:
        response = handler(mock_event, mock_lambda_context)
    except:
        print("Error running handler!")
        raise
    span = tracer.recorder.get_spans()[0]

    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['Sample Context']
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
    
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
    assert invocation_support.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['Sample Context']
