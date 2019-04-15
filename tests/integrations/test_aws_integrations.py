import os
import mock
import boto3
from boto3.exceptions import Boto3Error
from botocore.exceptions import BotoCoreError
from botocore.errorfactory import ClientError
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.invocation import invocation_support

from thundra import constants
from thundra.integrations.botocore import *

botocore_errors = (ClientError, Boto3Error, BotoCoreError)


def test_dynamodb():
    try:
        # Make a request over the table
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('test-table')
        table.get_item(
            Key={
                'username': 'janedoe',
                'age': 22,
                'colors': ['red', 'green', 'blue'],
                'numbers': [3, 7],
                'data': b'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                'others': [b'foo', b'bar'],
            }
        )

        # Make request over the client object
        dynamodb.get_item(
            TableName='test-table',
            Key={
                'username': {
                    'S': 'janedoe',
                },
                'age': {
                    'N': '22'
                },
                'colors': {
                    'SS': ['red', 'green', 'blue']
                },
                'numbers': {
                    'NS': ['3', '7']
                },
                'data': {
                    'B': b'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                },
                'others': {
                    'BS': [b'foo', b'bar'],
                },
            }
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        statements = [
            {
                'username': 'janedoe',
                'age': 22,
                'colors': ['red', 'green', 'blue'],
                'data': 'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                'numbers': [3, 7],
                'others': ['foo', 'bar']
            },
            {
                'username': {
                    'S': 'janedoe',
                },
                'age': {
                    'N': '22'
                },
                'colors': {
                    'SS': ['red', 'green', 'blue']
                },
                'numbers': {
                    'NS': ['3', '7']
                },
                'data': {
                    'B': 'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                },
                'others': {
                    'BS': ['foo', 'bar'],
                }
            }
        ]
        spans = tracer.get_spans()
        for i in range(len(spans)):
            span = spans[i]
            assert span.class_name == 'AWS-DynamoDB'
            assert span.domain_name == 'DB'
            assert span.operation_name == 'test-table'
            assert span.get_tag("operation.type") == 'READ'
            assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
            assert span.get_tag('db.statement') == statements[i]
            assert span.get_tag('db.statement.type') == 'READ'
            assert span.get_tag('db.type') == 'aws-dynamodb'
            assert span.get_tag('aws.dynamodb.table.name') == 'test-table'
        tracer.clear()


def test_dynamodb_put_item(monkeypatch):
    monkeypatch.setitem(os.environ, constants.ENABLE_DYNAMODB_TRACE_INJECTION, 'true')

    try:
        item = {
            'id': {'S': "3"},
            'text': {'S': "test2"}
        }

        dynamodb = boto3.client('dynamodb', region_name='eu-west-2')
        dynamodb.put_item(
            TableName="test-table",
            Item=item,
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.class_name == 'AWS-DynamoDB'
        assert span.domain_name == 'DB'
        assert span.operation_name == 'test-table'
        assert span.get_tag("operation.type") == 'WRITE'
        assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
        assert span.get_tag('db.statement') == item
        assert span.get_tag('db.statement.type') == 'WRITE'
        assert span.get_tag('db.type') == 'aws-dynamodb'
        assert span.get_tag('aws.dynamodb.table.name') == 'test-table'

        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ["SAVE:" + span.span_id]
        tracer.clear()


def test_dynamodb_put_item_resource(monkeypatch):
    monkeypatch.setitem(os.environ, constants.ENABLE_DYNAMODB_TRACE_INJECTION, 'true')

    try:
        item = {
            'id': '3',
            'text': 'test'
        }

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('test-table')
        table.put_item(
            TableName="test-table",
            Item=item,
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.class_name == 'AWS-DynamoDB'
        assert span.domain_name == 'DB'
        assert span.operation_name == 'test-table'
        assert span.get_tag("operation.type") == 'WRITE'
        assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
        assert span.get_tag('db.statement') == item
        assert span.get_tag('db.statement.type') == 'WRITE'
        assert span.get_tag('db.type') == 'aws-dynamodb'
        assert span.get_tag('aws.dynamodb.table.name') == 'test-table'

        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ["SAVE:" + span.span_id]
        tracer.clear()


def test_dynamodb_statement_mask(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_DYNAMODB_STATEMENT, 'true')
    try:
        # Make a request over the table
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('test-table')
        table.get_item(
            Key={
                'username': 'janedoe',
                'age': 22,
                'colors': ['red', 'green', 'blue'],
                'numbers': [3, 7],
                'data': b'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                'others': [b'foo', b'bar'],
            }
        )

        # Make request over the client object
        dynamodb.get_item(
            TableName='test-table',
            Key={
                'username': {
                    'S': 'janedoe',
                },
                'age': {
                    'N': '22'
                },
                'colors': {
                    'SS': ['red', 'green', 'blue']
                },
                'numbers': {
                    'NS': ['3', '7']
                },
                'data': {
                    'B': b'dGhpcyB0ZXh0IGlzIGJhc2U2NC1lbmNvZGVk',
                },
                'others': {
                    'BS': [b'foo', b'bar'],
                },
            }
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        spans = tracer.get_spans()
        for i in range(len(spans)):
            span = spans[i]
            assert span.class_name == 'AWS-DynamoDB'
            assert span.domain_name == 'DB'
            assert span.operation_name == 'test-table'
            assert span.get_tag("operation.type") == 'READ'
            assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
            assert span.get_tag('db.statement') == None
            assert span.get_tag('db.statement.type') == 'READ'
            assert span.get_tag('db.type') == 'aws-dynamodb'
            assert span.get_tag('aws.dynamodb.table.name') == 'test-table'
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_s3(mock_actual_call, mock_s3_response):
    mock_actual_call.return_value = mock_s3_response
    try:
        s3 = boto3.client('s3')
        s3.get_object(
            Bucket='test-bucket',
            Key='test.txt'
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-S3'
        assert span.domain_name == 'Storage'
        assert span.get_tag('operation.type') == 'READ'
        assert span.get_tag('aws.s3.bucket.name') == 'test-bucket'
        assert span.get_tag('aws.request.name') == 'GetObject'
        assert span.get_tag('aws.s3.object.name') == 'test.txt'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['C3D13FE58DE4C810']
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_lambda(mock_actual_call, mock_lambda_response, wrap_handler_with_thundra, mock_event, mock_context):
    mock_actual_call.return_value = mock_lambda_response

    def handler(event, context):
        lambdaFunc = boto3.client('lambda', region_name='us-west-2')
        lambdaFunc.invoke(
            FunctionName='Test',
            InvocationType='RequestResponse',
            Payload=b"{\"name\": \"thundra\"}"
        )

    tracer = ThundraTracer.get_instance()

    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        with mock.patch('thundra.reporter.Reporter.clear'):
            thundra, wrapped_handler = wrap_handler_with_thundra(handler)
            try:
                wrapped_handler(mock_event, mock_context)
            except:
                pass

            # Check span tags
            span = tracer.get_spans()[1]
            assert span.class_name == 'AWS-Lambda'
            assert span.domain_name == 'API'
            assert span.get_tag('aws.lambda.name') == 'Test'
            assert span.get_tag('aws.lambda.qualifier') is None
            assert span.get_tag('aws.lambda.invocation.payload') == "{\"name\": \"thundra\"}"
            assert span.get_tag('aws.request.name') == 'Invoke'
            assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'

            # Check report
            report = thundra.reporter.reports[3]['data']
            assert report['className'] == 'AWS-Lambda'
            assert report['domainName'] == 'API'
            assert report['tags']['aws.request.name'] == 'Invoke'
            assert report['tags']['operation.type'] == 'CALL'
            assert report['tags']['aws.lambda.name'] == 'Test'
            assert type(report['tags']['aws.lambda.invocation.payload']) == str
            assert report['tags']['aws.lambda.invocation.payload'] == "{\"name\": \"thundra\"}"
            assert report['tags']['aws.lambda.invocation.type'] == 'RequestResponse'
            assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['test-request-id']

    tracer.clear()
    invocation_support.function_name = ""

@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_lambda_payload_masked(mock_actual_call, mock_lambda_response, wrap_handler_with_thundra, mock_event, mock_context, monkeypatch):
    mock_actual_call.return_value = mock_lambda_response
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_LAMBDA_PAYLOAD, 'true')

    def handler(event, context):
        lambdaFunc = boto3.client('lambda', region_name='us-west-2')
        lambdaFunc.invoke(
            FunctionName='Test',
            InvocationType='RequestResponse',
            Payload=b"{\"name\": \"thundra\"}"
        )

    tracer = ThundraTracer.get_instance()

    with mock.patch('thundra.opentracing.recorder.ThundraRecorder.clear'):
        with mock.patch('thundra.reporter.Reporter.clear'):
            thundra, wrapped_handler = wrap_handler_with_thundra(handler)
            try:
                wrapped_handler(mock_event, mock_context)
            except:
                pass

            # Check span tags
            span = tracer.get_spans()[1]
            assert span.class_name == 'AWS-Lambda'
            assert span.domain_name == 'API'
            assert span.get_tag('aws.lambda.name') == 'Test'
            assert span.get_tag('aws.lambda.qualifier') is None
            assert span.get_tag('aws.lambda.invocation.payload') == None
            assert span.get_tag('aws.request.name') == 'Invoke'
            assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'
    tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_sqs(mock_actual_call, mock_sqs_response):
    mock_actual_call.return_value = mock_sqs_response
    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
        sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Thundra!',
            DelaySeconds=123,
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-SQS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSQSTags['MESSAGE']) == 'Hello Thundra!'
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_sqs_message_masked(mock_actual_call, mock_sqs_response, monkeypatch):
    mock_actual_call.return_value = mock_sqs_response
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_SQS_MESSAGE, 'true')
    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
        sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Thundra!',
            DelaySeconds=123,
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-SQS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSQSTags['MESSAGE']) == None
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_sns(mock_actual_call, mock_sns_response):
    mock_actual_call.return_value = mock_sns_response

    try:
        sns = boto3.client('sns', region_name='us-west-2')
        sns.publish(
            TopicArn='Test-topic',
            Message='Hello Thundra!',
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-SNS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSNSTags['MESSAGE']) == 'Hello Thundra!'
        tracer.clear()

@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_sns_message_masked(mock_actual_call, mock_sns_response, monkeypatch):
    mock_actual_call.return_value = mock_sns_response
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_SNS_MESSAGE, 'true')

    try:
        sns = boto3.client('sns', region_name='us-west-2')
        sns.publish(
            TopicArn='Test-topic',
            Message='Hello Thundra!',
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-SNS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSNSTags['MESSAGE']) == None
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_kinesis(mock_actual_call, mock_kinesis_response):
    mock_actual_call.return_value = mock_kinesis_response

    region = 'us-west-2'
    shard_id = 'shardId--000000000000'
    sequence_number = '49568167373333333333333333333333333333333333333333333333'

    try:
        kinesis = boto3.client('kinesis', region_name=region)
        kinesis.put_record(
            Data='STRING_VALUE',
            PartitionKey='STRING_VALUE',
            StreamName='STRING_VALUE',
            ExplicitHashKey='STRING_VALUE',
            SequenceNumberForOrdering='STRING_VALUE'
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-Kinesis'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.kinesis.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == [
            region + ':' + 'STRING_VALUE:' + shard_id + ':' + sequence_number]
        tracer.clear()


@mock.patch('thundra.integrations.botocore.BaseIntegration.actual_call')
def test_firehose(mock_actual_call, mock_firehose_response):
    mock_actual_call.return_value = mock_firehose_response
    region = 'us-west-2'
    timestamp = 1553695200
    md5 = "098f6bcd4621d373cade4e832627b4f6"
    links = [
        region + ":" + "test-stream" + ":" + str(timestamp) + ":" + md5,
        region + ":" + "test-stream" + ":" + str(timestamp + 1) + ":" + md5,
        region + ":" + "test-stream" + ":" + str(timestamp + 2) + ":" + md5
    ]
    try:
        firehose = boto3.client('firehose', region_name=region)
        firehose.put_record(
            DeliveryStreamName='test-stream',
            Record={
                'Data': 'test'
            }
        )
    except botocore_errors:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'AWS-Firehose'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.firehose.stream.name') == 'test-stream'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        assert sorted(span.get_tag(constants.SpanTags['TRACE_LINKS'])) == sorted(links)
        tracer.clear()


def test_kms():
    try:
        kms = boto3.client('kms', region_name='us-west-2')
        kms.update_key_description(
            KeyId='1234abcd-12ab-34cd-56ef-1234567890ab',
            Description='foo'
        )
        raise Exception("Shouldn't reach here")
    except botocore_errors:
        pass


def test_sqs_get_trace_links():
    response = {
        'MessageId': 'MessageID_1',
    }

    links = AWSSQSIntegration.get_trace_links('SendMessage', response)
    assert links == ['MessageID_1']


def test_sqs_get_trace_links_batch():
    response = {
        'Successful': [
            {
                'MessageId': 'MessageID_1',
            },
            {
                'MessageId': 'MessageID_2',
            },
        ]
    }

    links = AWSSQSIntegration.get_trace_links('SendMessageBatch', response)
    assert links == ['MessageID_1', 'MessageID_2']


def test_sns_get_trace_links():
    response = {
        'MessageId': 'MessageID_1'
    }

    links = AWSSNSIntegration.get_trace_links(response)
    assert links == ['MessageID_1']


def test_kinesis_get_trace_links_put_record():
    response = {
        'ShardId': 'shardId--000000000000',
        'SequenceNumber': '49568167373333333333333333333333333333333333333333333333'
    }

    integration = AWSKinesisIntegration()
    integration.streamName = 'test-stream'
    region = 'eu-west-2'
    links = integration.get_trace_links(region, response)
    assert links == [region + ':' + 'test-stream' + ':' + response['ShardId'] + ':' + response['SequenceNumber']]


def test_kinesis_get_trace_links_put_records():
    sequence_number = '49568167373333333333333333333333333333333333333333333333'
    shard_id = 'shardId--000000000000'
    response = {
        'Records': [
            {
                'SequenceNumber': sequence_number,
                'ShardId': shard_id,
            },
        ],
    }

    integration = AWSKinesisIntegration()
    integration.streamName = 'test-stream'
    region = 'eu-west-2'
    links = integration.get_trace_links(region, response)
    assert links == [region + ':' + 'test-stream' + ':' + shard_id + ':' + sequence_number]


def test_firehose_get_trace_links_put_record_batch():
    response = {"ResponseMetadata": {"HTTPHeaders": {"date": "Wed, 27 Mar 2019 14:00:00 GMT"}}}
    request = {"Records": [{"Data": b'bytes'}]}
    args = ["PutRecordBatch", request]

    integration = AWSFirehoseIntegration()
    integration.deliveryStreamName = "test-stream"
    region = "us-west-2"

    links = integration.get_trace_links(args, region, response)
    timestamp = 1553695200
    md5 = "4b3a6218bb3e3a7303e8a171a60fcf92"
    assert links == [
        region + ":" + "test-stream" + ":" + str(timestamp) + ":" + md5,
        region + ":" + "test-stream" + ":" + str(timestamp + 1) + ":" + md5,
        region + ":" + "test-stream" + ":" + str(timestamp + 2) + ":" + md5
    ]
