from thundra.opentracing.tracer import ThundraTracer
import boto3
import mock


def test_dynamodb():
    try:
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('test-table')
        table.get_item(
            Key={
                'username': 'janedoe',
                'last_name': 'Doe'
            }
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-DynamoDB'
        assert span.domain_name == 'DB'
        assert span.operation_name == 'test-table'
        assert span.get_tag("operation.type") == 'READ'
        assert span.get_tag("db.instance") == 'dynamodb.eu-west-2.amazonaws.com'
        assert span.get_tag('db.statement') == {'username': 'janedoe', 'last_name': 'Doe'}
        assert span.get_tag('db.statement.type') == 'READ'
        assert span.get_tag('db.type') == 'aws-dynamodb'
        assert span.get_tag('aws.dynamodb.table.name') == 'test-table'
        tracer.clear()


def test_s3():
    try:
        s3 = boto3.client('s3')
        s3.get_object(
            Bucket='test-bucket',
            Key='test.txt'
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-S3'
        assert span.domain_name == 'Storage'
        assert span.get_tag('operation.type') == 'READ'
        assert span.get_tag('aws.s3.bucket.name') == 'test-bucket'
        assert span.get_tag('aws.request.name') == 'GetObject'
        assert span.get_tag('aws.s3.object.name') == 'test.txt'
        tracer.clear()

def test_lambda(wrap_handler_with_thundra, mock_event, mock_context):
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
            span = tracer.recorder.finished_span_stack[0]
            assert span.class_name == 'AWS-Lambda'
            assert span.domain_name == 'API'
            assert span.get_tag('aws.lambda.name') == 'Test'
            assert span.get_tag('aws.lambda.qualifier') is None
            assert span.get_tag('aws.lambda.invocation.payload') == "{\"name\": \"thundra\"}"
            assert span.get_tag('aws.request.name') == 'Invoke'
            assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'

            # Check report
            report = thundra.reporter.reports[2]['data']
            assert report['className'] == 'AWS-Lambda'
            assert report['domainName'] == 'API'
            assert report['tags']['aws.request.name'] == 'Invoke'
            assert report['tags']['operation.type'] == 'CALL'
            assert report['tags']['aws.lambda.name'] == 'Test'
            assert type(report['tags']['aws.lambda.invocation.payload']) == str
            assert report['tags']['aws.lambda.invocation.payload'] == "{\"name\": \"thundra\"}"
            assert report['tags']['aws.lambda.invocation.type'] == 'RequestResponse'
    
    tracer.clear()


def test_sqs():
    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
        sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Thundra!',
            DelaySeconds=123,
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-SQS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        tracer.clear()


def test_sns():
    try:
        sns = boto3.client('sns', region_name='us-west-2')
        sns.publish(
            TopicArn='Test-topic',
            Message='Hello Thundra!',
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-SNS'
        assert span.domain_name == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        tracer.clear()


def test_kinesis():
    try:
        kinesis = boto3.client('kinesis', region_name='us-west-2')
        kinesis.put_record(
            Data='STRING_VALUE',
            PartitionKey='STRING_VALUE',
            StreamName='STRING_VALUE',
            ExplicitHashKey='STRING_VALUE',
            SequenceNumberForOrdering='STRING_VALUE'
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-Kinesis'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.kinesis.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        tracer.clear()


def test_firehose():
    try:
        firehose = boto3.client('firehose', region_name='us-west-2')
        firehose.put_record(
            DeliveryStreamName='STRING_VALUE',
            Record={
                'Data': 'STRING_VALUE'
            }
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[0]
        assert span.class_name == 'AWS-Firehose'
        assert span.domain_name == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.firehose.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        tracer.clear()
