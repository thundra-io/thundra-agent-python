import os

from thundra.opentracing.tracer import ThundraTracer
import mock
import boto3

def test_dynamodb(dynamodb_handler, mock_context, mock_event):

    thundra, handler = dynamodb_handler
    # print(vars(mock_context))
    try:
        dynamodb = boto3.resource('dynamodb')
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
    assert span.className is 'AWS-DynamoDB'
    assert span.domainName is 'DB'