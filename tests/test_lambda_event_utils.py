import mock
import base64
import gzip
import json
from thundra import lambda_event_utils, constants
from thundra.opentracing.tracer import ThundraTracer


def test_dynamodb_trigger(handler, mock_dynamodb_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_dynamodb_event, mock_context) == lambda_event_utils.LambdaEventType.DynamoDB
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_dynamodb_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['DB']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['DYNAMODB']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTableWithStream']
    finally:
        tracer.clear()


def test_sqs_trigger(handler, mock_sqs_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_sqs_event, mock_context) == lambda_event_utils.LambdaEventType.SQS
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_sqs_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SQS']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['MyQueue']
    finally:
        tracer.clear()


def test_sns_trigger(handler, mock_sns_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_sns_event, mock_context) == lambda_event_utils.LambdaEventType.SNS
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_sns_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['MESSAGING']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['SNS']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleTopic']
    finally:
        tracer.clear()


def test_kinesis_trigger(handler, mock_kinesis_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_kinesis_event, mock_context) == lambda_event_utils.LambdaEventType.Kinesis
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_kinesis_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['KINESIS']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example_stream']
    finally:
        tracer.clear()


def test_cloudwatch_schedule_trigger(handler, mock_cloudwatch_schedule_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_cloudwatch_schedule_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.CloudWatchSchedule
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_cloudwatch_schedule_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Schedule'
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Schedule'
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['ExampleRule']
    finally:
        tracer.clear()


def test_cloudwatch_logs_trigger(handler, mock_cloudwatch_logs_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_cloudwatch_logs_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.CloudWatchLogs
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_cloudwatch_logs_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'Log'
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudWatch-Log'
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            compressed_data = base64.b64decode(mock_cloudwatch_logs_event['awslogs']['data'])
            decompressed_data = json.loads(str(gzip.decompress(compressed_data), 'utf-8'))
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [decompressed_data['logGroup']]
    finally:
        tracer.clear()


def test_cloudfront_event_trigger(handler, mock_cloudfront_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_cloudfront_event, mock_context) == lambda_event_utils.LambdaEventType.CloudFront
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_cloudfront_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'CDN'
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-CloudFront'
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['/test']
    finally:
        tracer.clear()


def test_firehose_trigger(handler, mock_firehose_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_firehose_event, mock_context) == lambda_event_utils.LambdaEventType.Firehose
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_firehose_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STREAM']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['FIREHOSE']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['exampleStream']
    finally:
        tracer.clear()


def test_apigateway_proxy_trigger(handler, mock_apigateway_proxy_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_apigateway_proxy_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.APIGatewayProxy
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_apigateway_proxy_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
                '1234567890.execute-api.eu-west-2.amazonaws.com/prod/path/to/resource']
    finally:
        tracer.clear()


def test_apigateway_trigger(handler, mock_apigateway_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_apigateway_event,
                                                    mock_context) == lambda_event_utils.LambdaEventType.APIGateway
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_apigateway_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-APIGateway'
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == [
                'random.execute-api.us-west-2.amazonaws.com/dev{}']
    finally:
        tracer.clear()


def test_s3_trigger(handler, mock_s3_event, mock_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_s3_event, mock_context) == lambda_event_utils.LambdaEventType.S3
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_s3_event, mock_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['STORAGE']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['S3']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['example-bucket']
    finally:
        tracer.clear()


def test_lambda_trigger(handler, mock_event, mock_lambda_context):
    thundra, handler = handler
    tracer = ThundraTracer.get_instance()
    try:
        assert lambda_event_utils.get_lambda_event_type(mock_event, mock_lambda_context) == lambda_event_utils.LambdaEventType.Lambda
        with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
            try:
                response = handler(mock_event, mock_lambda_context)
            except:
                print("Error running handler!")
                raise
            span = tracer.recorder.get_spans()[0]

            assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.DomainNames['API']
            assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.ClassNames['LAMBDA']
            assert constants.SpanTags['TOPOLOGY_VERTEX']
            assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['Sample Context']
    finally:
        tracer.clear()