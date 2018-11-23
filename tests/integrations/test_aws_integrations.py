from thundra.opentracing.tracer import ThundraTracer
import boto3


def test_dynamodb():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-table')
        table.get_item(
            Key={
                'username': 'janedoe',
                'last_name': 'Doe'
            }
        )
        # response = handler(mock_event, mock_context)
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        # print (type(span.className))
        assert span.className == 'AWS-DynamoDB'
        assert span.domainName == 'DB'
        assert span.operationName == 'GetItem'
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
        response = s3.get_object(
            Bucket='test-bucket',
            Key='test.txt'
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        assert span.className == 'AWS-S3'
        assert span.domainName == 'Storage'
        assert span.get_tag('operation.type') == 'READ'
        assert span.get_tag('aws.s3.bucket.name') == 'test-bucket'
        assert span.get_tag('aws.request.name') == 'GetObject'
        assert span.get_tag('aws.s3.object.name') == 'test.txt'
        tracer.clear()


def test_lambda():
    try:
        lambdaFunc = boto3.client('lambda')
        response = lambdaFunc.invoke(
            FunctionName='Test',
            InvocationType='RequestResponse',
            Payload={"name": "thundra"}
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[2]
        # print(vars(span))
        assert span.className == 'AWS-Lambda'
        assert span.domainName == 'API'
        assert span.get_tag('aws.lambda.function.name') == 'Test'
        assert span.get_tag('aws.lambda.function.qualifier') is None
        assert span.get_tag('aws.lambda.invocation.payload') == {"name": "thundra"}
        assert span.get_tag('aws.request.name') == 'Invoke'
        assert span.get_tag('aws.lambda.invocation.type') == 'RequestResponse'
        tracer.clear()


def test_sqs():
    try:
        sqs = boto3.client('sqs')
        response = sqs.send_message(
            QueueUrl='test-queue',
            MessageBody='Hello Thundra!',
            DelaySeconds=123,
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        assert span.className == 'AWS-SQS'
        assert span.domainName == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sqs.queue.name') == 'test-queue'
        assert span.get_tag('aws.request.name') == 'SendMessage'
        tracer.clear()


def test_sns():
    try:
        sns = boto3.client('sns')
        response = sns.publish(
            TopicArn='Test-topic',
            Message='Hello Thundra!',
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        assert span.className == 'AWS-SNS'
        assert span.domainName == 'Messaging'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.sns.topic.name') == 'Test-topic'
        assert span.get_tag('aws.request.name') == 'Publish'
        tracer.clear()


def test_kinesis():
    try:
        kinesis = boto3.client('kinesis')
        response = kinesis.put_record(
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
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        assert span.className == 'AWS-Kinesis'
        assert span.domainName == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.kinesis.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        tracer.clear()


def test_kinesis():
    try:
        firehose = boto3.client('firehose')
        response = firehose.put_record(
            DeliveryStreamName='STRING_VALUE',
            Record={
                'Data': 'STRING_VALUE'
            }
        )
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        # print(vars(span))
        assert span.className == 'AWS-Firehose'
        assert span.domainName == 'Stream'
        assert span.get_tag('operation.type') == 'WRITE'
        assert span.get_tag('aws.firehose.stream.name') == 'STRING_VALUE'
        assert span.get_tag('aws.request.name') == 'PutRecord'
        tracer.clear()
