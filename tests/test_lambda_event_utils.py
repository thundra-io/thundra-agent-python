from thundra.opentracing.tracer import ThundraTracer
# import boto3
import mock
from thundra.lambda_event_utils import LambdaEventUtils
from thundra.lambda_event_utils import LambdaEventType
from thundra import constants
import base64
import gzip
import json


def test_dynamodb_trigger(handler, mock_dynamodb_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_dynamodb_event, mock_context) == LambdaEventType.DynamoDB
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_dynamodb_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']

    tracer.clear()


def test_sqs_trigger(handler, mock_sqs_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_sqs_event, mock_context) == LambdaEventType.SQS
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_sqs_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']

    tracer.clear()


def test_sns_trigger(handler, mock_sns_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_sns_event, mock_context) == LambdaEventType.SNS
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_sns_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']

    tracer.clear()


def test_kinesis_trigger(handler, mock_kinesis_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_kinesis_event, mock_context) == LambdaEventType.Kinesis
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_kinesis_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']

    tracer.clear()


def test_cloudwatch_schedule_trigger(handler, mock_cloudwatch_schedule_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_cloudwatch_schedule_event,
                                                  mock_context) == LambdaEventType.CloudWatchSchedule
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_cloudwatch_schedule_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']

    tracer.clear()


def test_cloudwatch_logs_trigger(handler, mock_cloudwatch_logs_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_cloudwatch_logs_event,
                                                  mock_context) == LambdaEventType.CloudWatchLogs
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_cloudwatch_logs_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        compressed_data = base64.b64decode(mock_cloudwatch_logs_event['awslogs']['data'])
        decompressed_data = json.loads(str(gzip.decompress(compressed_data), 'utf-8'))
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [decompressed_data['logGroup']]

    tracer.clear()


def test_cloudfront_event_trigger(handler, mock_cloudfront_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_cloudfront_event, mock_context) == LambdaEventType.CloudFront
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_cloudfront_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']

    tracer.clear()


def test_firehose_trigger(handler, mock_firehose_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_firehose_event, mock_context) == LambdaEventType.Firehose
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_firehose_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['FIREHOSE']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']

    tracer.clear()


def test_apigateway_proxy_trigger(handler, mock_apigateway_proxy_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_apigateway_proxy_event,
                                                  mock_context) == LambdaEventType.APIGatewayProxy
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_apigateway_proxy_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
            '1234567890.execute-api.eu-west-2.amazonaws.com/prod/path/to/resource']

    tracer.clear()


def test_apigateway_trigger(handler, mock_apigateway_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_apigateway_event,
                                                  mock_context) == LambdaEventType.APIGateway
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_apigateway_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
            'random.execute-api.us-west-2.amazonaws.com/dev{}']

    tracer.clear()


def test_s3_trigger(handler, mock_s3_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_s3_event, mock_context) == LambdaEventType.S3
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_s3_event, mock_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STORAGE']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']

    tracer.clear()


def test_lambda_trigger(handler, mock_event, mock_lambda_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    assert LambdaEventUtils.get_lambda_event_type(mock_event, mock_lambda_context) == LambdaEventType.Lambda
    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        try:
            response = handler(mock_event, mock_lambda_context)
        except:
            print("Error running handler!")
            raise
        span = tracer.recorder.finished_span_stack[0]

        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
        assert constants.SpanTags['TOPOLOGY_VERTEX']
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == 'Sample Context'

    tracer.clear()