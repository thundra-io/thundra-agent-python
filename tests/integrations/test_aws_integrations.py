import boto3
import mock
from boto3.exceptions import Boto3Error
from botocore.errorfactory import ClientError
from botocore.exceptions import BotoCoreError

from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.integrations.botocore import *
from catchpoint.opentracing.tracer import CatchpointTracer

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
        tracer = CatchpointTracer.get_instance()
        spans = tracer.get_spans()[1:]
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


def test_dynamodb_put_item():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE, 'true')
    item = {
        'id': {'S': "3"},
        'text': {'S': "test2"}
    }
    try:
        dynamodb = boto3.client('dynamodb', region_name='eu-west-2')
        dynamodb.put_item(
            TableName="test-table",
            Item=item,
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

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


def test_dynamodb_put_item_resource():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE, 'true')
    item = {
        'id': '3',
        'text': 'test'
    }
    try:
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('test-table')
        table.put_item(
            TableName="test-table",
            Item=item,
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

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


def test_dynamodb_statement_mask():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_STATEMENT_MASK, 'true')
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
        tracer = CatchpointTracer.get_instance()
        spans = tracer.get_spans()[1:]

        for i in range(len(spans)):
            span = spans[i]
            assert span.class_name == 'AWS-DynamoDB'
            assert span.domain_name == 'DB'
            assert span.operation_name == 'test-table'
            assert span.get_tag("operation.type") == 'READ'
            assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
            assert span.get_tag('db.statement') is None
            assert span.get_tag('db.statement.type') == 'READ'
            assert span.get_tag('db.type') == 'aws-dynamodb'
            assert span.get_tag('aws.dynamodb.table.name') == 'test-table'


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
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
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-S3'
        assert span.domain_name == 'Storage'
        assert span.get_tag('operation.type') == 'READ'
        assert span.get_tag('aws.s3.bucket.name') == 'test-bucket'
        assert span.get_tag('aws.request.name') == 'GetObject'
        assert span.get_tag('aws.s3.object.name') == 'test.txt'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['C3D13FE58DE4C810']


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_lambda(mock_actual_call, mock_lambda_response, wrap_handler_with_catchpoint, mock_event, mock_context):
    mock_actual_call.return_value = mock_lambda_response

    def handler(event, context):
        lambda_func = boto3.client('lambda', region_name='us-west-2')
        lambda_func.invoke(
            FunctionName='Test',
            InvocationType='RequestResponse',
            Payload=b"{\"name\": \"catchpoint\"}"
        )

    with mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder.clear'):
        _, wrapped_handler = wrap_handler_with_catchpoint(handler)
        try:
            wrapped_handler(mock_event, mock_context)
        except:
            pass

        # Check span tags
        execution_context = ExecutionContextManager.get()
        span = execution_context.recorder.get_spans()[1]
        assert span.class_name == 'AWS-Lambda'
        assert span.domain_name == 'API'
        assert span.get_tag('aws.lambda.name') == 'Test'
        assert span.get_tag('aws.lambda.qualifier') is None
        assert span.get_tag('aws.lambda.invocation.payload') == "{\"name\": \"catchpoint\"}"
        assert span.get_tag('aws.request.name') == 'Invoke'
        assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'

        # Check report
        report = execution_context.reports[2]['data']
        assert report['className'] == 'AWS-Lambda'
        assert report['domainName'] == 'API'
        assert report['tags']['aws.request.name'] == 'Invoke'
        assert report['tags']['operation.type'] == 'WRITE'
        assert report['tags']['aws.lambda.name'] == 'Test'
        assert type(report['tags']['aws.lambda.invocation.payload']) == str
        assert report['tags']['aws.lambda.invocation.payload'] == "{\"name\": \"catchpoint\"}"
        assert report['tags']['aws.lambda.invocation.type'] == 'RequestResponse'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['test-request-id']


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_lambda_noninvoke_function(mock_actual_call, mock_lambda_response, wrap_handler_with_catchpoint, mock_event,
                                   mock_context):
    mock_actual_call.return_value = mock_lambda_response

    def handler(event, context):
        lambdaFunc = boto3.client('lambda', region_name='us-west-2')
        lambdaFunc.list_functions()

    tracer = CatchpointTracer.get_instance()

    with mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder.clear'):
        _, wrapped_handler = wrap_handler_with_catchpoint(handler)
        try:
            wrapped_handler(mock_event, mock_context)
        except:
            pass

        # Check span tags
        execution_context = ExecutionContextManager.get()
        span = execution_context.recorder.get_spans()[1]
        assert span.class_name == 'AWS-Lambda'
        assert span.domain_name == 'API'
        assert span.get_tag('aws.lambda.name') == ''
        assert span.get_tag('aws.lambda.qualifier') is None
        assert span.get_tag('aws.lambda.invocation.payload') is None
        assert span.get_tag('aws.request.name') == 'ListFunctions'
        assert span.get_tag('aws.lambda.invocation.type') is None

        # Check report
        report = execution_context.reports[2]['data']
        assert report['className'] == 'AWS-Lambda'
        assert report['domainName'] == 'API'
        assert report['tags']['aws.request.name'] == 'ListFunctions'
        assert report['tags']['operation.type'] == 'LIST'
        assert report['tags']['aws.lambda.name'] == ''
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['test-request-id']


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_lambda_payload_masked(mock_actual_call, mock_lambda_response, wrap_handler_with_catchpoint, mock_event,
                               mock_context):
    mock_actual_call.return_value = mock_lambda_response
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_LAMBDA_PAYLOAD_MASK, 'true')

    def handler(event, context):
        lambda_func = boto3.client('lambda', region_name='us-west-2')
        lambda_func.invoke(
            FunctionName='Test',
            InvocationType='RequestResponse',
            Payload=b"{\"name\": \"catchpoint\"}"
        )

    with mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder.clear'):
        _, wrapped_handler = wrap_handler_with_catchpoint(handler)
        try:
            wrapped_handler(mock_event, mock_context)
        except:
            pass

        # Check span tags
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Lambda'
        assert span.domain_name == 'API'
        assert span.get_tag('aws.lambda.name') == 'Test'
        assert span.get_tag('aws.lambda.qualifier') is None
        assert span.get_tag('aws.lambda.invocation.payload') is None
        assert span.get_tag('aws.request.name') == 'Invoke'
        assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_sqs(mock_actual_call, mock_sqs_response):
    mock_actual_call.return_value = mock_sqs_response
    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
        sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Catchpoint!',
            DelaySeconds=123,
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SQS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSQSTags['MESSAGE']) == 'Hello Catchpoint!'


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_sqs_message_masked(mock_actual_call, mock_sqs_response):
    mock_actual_call.return_value = mock_sqs_response
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_SQS_MESSAGE_MASK, 'true')
    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
        sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Catchpoint!',
            DelaySeconds=123,
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SQS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSQSTags['MESSAGE']) is None


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_sns(mock_actual_call, mock_sns_response):
    mock_actual_call.return_value = mock_sns_response

    try:
        sns = boto3.client('sns', region_name='us-west-2')
        sns.publish(
            TopicArn='Test-topic',
            Message='Hello Catchpoint!',
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SNS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSNSTags['MESSAGE']) == 'Hello Catchpoint!'


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_sns_message_masked(mock_actual_call, mock_sns_response):
    mock_actual_call.return_value = mock_sns_response
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_SNS_MESSAGE_MASK, 'true')

    try:
        sns = boto3.client('sns', region_name='us-west-2')
        sns.publish(
            TopicArn='Test-topic',
            Message='Hello Catchpoint!',
        )
    except botocore_errors:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SNS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['MessageID_1']
        assert span.get_tag(constants.AwsSNSTags['MESSAGE']) is None


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
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
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Kinesis'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.kinesis.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == [
            region + ':' + 'STRING_VALUE:' + shard_id + ':' + sequence_number]


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
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
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Firehose'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.firehose.stream.name') == 'test-stream'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        assert sorted(span.get_tag(constants.SpanTags['TRACE_LINKS'])) == sorted(links)


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


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_athena_start_query_execution(mock_actual_call, mock_athena_start_query_exec_response):
    mock_actual_call.return_value = mock_athena_start_query_exec_response

    database = "test"
    table = "persons"
    query = "SELECT * FROM %s.%s where age = 10;" % (database, table)
    s3_output = 's3://athena-test-bucket/results/'

    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': s3_output,
            }
        )
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'StartQueryExecution'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == database
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) == s3_output
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) == [
            "98765432-1111-1111-1111-12345678910"]
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) == query


def test_athena_statement_masked():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_AWS_ATHENA_STATEMENT_MASK, 'true')

    database = "test"
    table = "persons"
    query = "SELECT * FROM %s.%s where age = 10;" % (database, table)
    s3_output = 's3://athena-test-bucket/results/'

    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': s3_output,
            }
        )
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'StartQueryExecution'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == database
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) == s3_output
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_stop_query_execution():
    query_execution_id = "98765432-1111-1111-1111-12345678910"
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.stop_query_execution(
            QueryExecutionId=query_execution_id
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'StopQueryExecution'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) == [query_execution_id]
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_batch_get_named_query():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.batch_get_named_query(
            NamedQueryIds=[
                'test',
            ]
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'BatchGetNamedQuery'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) == ["test"]
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_batch_get_query_execution():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.batch_get_query_execution(
            QueryExecutionIds=[
                'test',
                'test2'
            ]
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'BatchGetQueryExecution'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert sorted(span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS'])) == ['test', 'test2']
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_athena_create_named_query(mock_actual_call, mock_athena_create_named_query_response):
    mock_actual_call.return_value = mock_athena_create_named_query_response
    query = "SELECT * FROM persons where age = 10;"

    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.create_named_query(
            QueryString=query,
            Database="test",
            Name="test",
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'CreateNamedQuery'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) == ["98765432-1111-1111-1111-12345678910"]
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) == query


def test_athena_delete_named_query():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.delete_named_query(
            NamedQueryId='98765432-1111-1111-1111-12345678910'
        )

    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'DeleteNamedQuery'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) == ['98765432-1111-1111-1111-12345678910']
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_get_named_query():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.get_named_query(
            NamedQueryId='98765432-1111-1111-1111-12345678910'
        )

    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'GetNamedQuery'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) == ['98765432-1111-1111-1111-12345678910']
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_get_query_execution():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.get_query_execution(
            QueryExecutionId='98765432-1111-1111-1111-12345678910'
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'GetQueryExecution'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) == [
            '98765432-1111-1111-1111-12345678910']
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_athena_get_query_results():
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.get_query_results(
            QueryExecutionId='98765432-1111-1111-1111-12345678910'
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'GetQueryResults'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) == [
            '98765432-1111-1111-1111-12345678910']
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_eventbridge_put_events(mock_actual_call, mock_eventbridge_put_events_response):
    mock_actual_call.return_value = mock_eventbridge_put_events_response

    try:
        client = boto3.client('events', region_name='us-west-2')
        client.put_events(
            Entries=[
                {
                    'Time': datetime(2020, 1, 1),
                    'Source': 'test.aws.lambda',
                    'Resources': [
                        'test',
                    ],
                    'DetailType': 'mydetail',
                    'Detail': '{}',
                    'EventBusName': 'default'
                },
            ]
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == constants.ClassNames['EVENTBRIDGE']
        assert span.domain_name == constants.DomainNames['MESSAGING']
        assert span.operation_name == 'default'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsEventBridgeTags['ENTRIES']) == [{
            'Time': datetime.timestamp(datetime(2020, 1, 1)),
            'Source': 'test.aws.lambda',
            'Resources': [
                'test',
            ],
            'DetailType': 'mydetail',
            'Detail': '{}',
            'EventBusName': 'default'
        }]
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'PutEvents'
        assert span.get_tag(constants.SpanTags['RESOURCE_NAMES']) == ['mydetail']
        assert span.get_tag(constants.SpanTags['TRACE_LINKS']) == ['test-event-id']


@mock.patch('catchpoint.integrations.botocore.BaseIntegration.actual_call')
def test_athena_list_query_executions(mock_actual_call, mock_athena_list_query_executions_response):
    mock_actual_call.return_value = mock_athena_list_query_executions_response
    try:
        client = boto3.client('athena', region_name='us-west-2')
        client.list_query_executions(
            NextToken='string',
            MaxResults=123,
            WorkGroup='string'
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-Athena'
        assert span.domain_name == 'DB'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'LIST'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'ListQueryExecutions'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) is None
        assert span.get_tag(constants.AthenaTags['S3_OUTPUT_LOCATION']) is None
        assert span.get_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS']) == [
            '98765432-1111-1111-1111-12345678910']
        assert span.get_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS']) is None
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None


def test_ses_send_email():
    sender = 'testsender'
    recipient = 'testrecipient'
    cc = 'testcc'
    subject = 'testsubject'
    text = 'testbody'
    try:
        # Test with a non traced service client
        client = boto3.client('ses', region_name='us-west-2')
        client.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [
                    recipient
                ],
                'CcAddresses': [
                    cc
                ]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SES'
        assert span.domain_name == 'Messaging'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'SendEmail'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSESTags['SOURCE']) == sender
        assert span.get_tag(constants.AwsSESTags['DESTINATION']).get('ToAddresses', []).index(recipient) == 0
        assert span.get_tag(constants.AwsSESTags['DESTINATION']).get('CcAddresses', []).index(cc) == 0
        assert span.get_tag(constants.AwsSESTags['SUBJECT']) is None
        assert span.get_tag(constants.AwsSESTags['BODY']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_NAME']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_ARN']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_DATA']) is None


def test_ses_send_raw_email():
    sender = 'testsender'
    recipient = 'testrecipient'
    text = 'testbody'
    try:
        # Test with a non traced service client
        client = boto3.client('ses', region_name='us-west-2')
        client.send_raw_email(
            Source=sender,
            Destinations=[
                recipient
            ],
            RawMessage={
                'Text': {
                    'Data': text,
                    'Charset': 'UTF-8'
                }
            }
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SES'
        assert span.domain_name == 'Messaging'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'SendRawEmail'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSESTags['SOURCE']) == sender
        assert span.get_tag(constants.AwsSESTags['DESTINATION']).index(recipient) == 0
        assert span.get_tag(constants.AwsSESTags['SUBJECT']) is None
        assert span.get_tag(constants.AwsSESTags['BODY']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_NAME']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_ARN']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_DATA']) is None


def test_ses_send_templated_email():
    sender = 'testsender'
    recipient = 'testrecipient'
    template_name = 'testname'
    template_data = '{"test": "test"}'
    template_arn = 'testarn'
    try:
        # Test with a non traced service client
        client = boto3.client('ses', region_name='us-west-2')
        client.send_templated_email(
            Source=sender,
            Destination={
                'ToAddresses': [
                    recipient
                ]
            },
            Template=template_name,
            TemplateData=template_data,
            TemplateArn=template_arn
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-SES'
        assert span.domain_name == 'Messaging'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'SendTemplatedEmail'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.AwsSESTags['SOURCE']) == sender
        assert span.get_tag(constants.AwsSESTags['DESTINATION']).get('ToAddresses', []).index(recipient) == 0
        assert span.get_tag(constants.AwsSESTags['SUBJECT']) is None
        assert span.get_tag(constants.AwsSESTags['BODY']) is None
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_NAME']) == template_name
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_ARN']) == template_arn
        assert span.get_tag(constants.AwsSESTags['TEMPLATE_DATA']) is None


def test_default_aws_service():
    try:
        # Test with a non traced service client
        client = boto3.client('mediastore', region_name='us-west-2')
        client.create_container(
            ContainerName='string'
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWSService'
        assert span.domain_name == 'AWS'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'CreateContainer'
        assert span.get_tag(constants.AwsSDKTags['SERVICE_NAME']) == 'mediastore'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'


def test_sfn():
    ConfigProvider.set(config_names.CATCHPOINT_LAMBDA_AWS_STEPFUNCTIONS, 'true')
    try:
        client = boto3.client('stepfunctions', region_name='us-west-2')
        client.start_execution(
            stateMachineArn='string',
            name='string',
            input='{}'
        )
    except Exception as e:
        print(e)
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'AWS-StepFunctions'
        assert span.domain_name == 'AWS'
        assert span.get_tag(constants.AwsSDKTags['REQUEST_NAME']) == 'StartExecution'
        assert span.get_tag(constants.AwsSDKTags['SERVICE_NAME']) == 'sfn'


def test_get_operation_type():
    assert get_operation_type("AWS-Lambda", "ListTags") == "READ"
    assert get_operation_type("AWS-S3", "PutAccountPublicAccessBlock") == "PERMISSION"
    assert get_operation_type("AWSService", "CreateContainer") == "WRITE"
    assert get_operation_type("InvalidService", "InvalidOperation") == ""
    assert get_operation_type("AWS-SSM", "DescribeDocumentPermission") == "READ"
