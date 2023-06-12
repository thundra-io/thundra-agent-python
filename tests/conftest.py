import mock
import pytest

import catchpoint.constants as constants
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.context.execution_context import ExecutionContext
from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.context.global_execution_context_provider import GlobalExecutionContextProvider
from catchpoint.plugins.invocation import invocation_support
from catchpoint.reporter import Reporter
from catchpoint.catchpoint_agent import Catchpoint


class MockContext:
    memory_limit_in_mb = '128'
    log_group_name = 'log_group_name'
    log_stream_name = 'log_stream_name[]id'
    aws_request_id = 'aws_request_id'
    invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789123:function:test'
    function_version = 'function_version'

    def __init__(self, f_name='test_func'):
        self.function_name = f_name
        self.memory_limit_in_mb = '128'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name[]id'
        self.aws_request_id = 'aws_request_id'
        self.invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789123:function:test'
        self.function_version = 'function_version'


class LambdaTriggeredMockContext:
    memory_limit_in_mb = '128'
    log_group_name = 'log_group_name'
    log_stream_name = 'log_stream_name[]id'
    aws_request_id = 'aws_request_id'
    invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789123:function:test'
    function_version = 'function_version'

    def __init__(self, f_name='test_func'):
        self.function_name = f_name
        self.memory_limit_in_mb = '128'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name[]id'
        self.aws_request_id = 'aws_request_id'
        self.invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789123:function:test'
        self.function_version = 'function_version'
        self.client_context = type('', (), {})()
        self.client_context.custom = {
            constants.TRIGGER_OPERATION_NAME_KEY: 'Sample Context'
        }


@pytest.fixture(scope="session", autouse=True)
def set_execution_context_provider():
    ExecutionContextManager.set_provider(GlobalExecutionContextProvider())


@pytest.fixture(autouse=True)
def teardown():
    yield
    ConfigProvider.clear()
    ExecutionContextManager.set(ExecutionContext())


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def mock_lambda_context():
    return LambdaTriggeredMockContext()


@pytest.fixture
def mock_event():
    event = {
        'message': 'Hello'
    }
    return event


@pytest.fixture()
def mock_report():
    return {
        'apiKey': 'api key',
        'type': 'type',
        'dataFormatVersion': '1.1.1',
        'data': {
            'response': b'\xff\xd8\xff\xe0\x00\x10JFIF\x00'
        }
    }


@pytest.fixture()
def mock_report_with_byte_field():
    return {
        'apiKey': 'api key',
        'type': 'bytes',
        'dataFormatVersion': '1.1.1',
        'data': b'byte_data'
    }


@pytest.fixture()
def mock_invocation_report():
    return {
        "apiKey": "api key",
        "type": "Invocation",
        "dataModelVersion": "2.0",
        "data": {
            "id": "testid",
            "type": "Invocation",
            "agentVersion": "2.2.5",
            "dataModelVersion": "2.0",
            "traceId": "testtraceId",
            "transactionId": "testtransactionId",
            "spanId": "testspanId",
            "applicationPlatform": "AWS-Lambda",
            "functionName": "",
            "applicationRegion": "us-west-2",
            "duration": 1000,
            "startTimestamp": 1554193011000,
            "finishTimestamp": 1554193012000,
            "erroneous": False,
            "errorType": "",
            "errorMessage": "",
            "errorCode": -1,
            "coldStart": True,
            "timeout": False,
            "tags": {
                "aws.region": "us-west-2",
                "aws.lambda.name": "test",
                "aws.lambda.arn": "arn:aws:lambda:us-west-2:123456789101:function:test",
                "aws.lambda.memory_limit": 512,
                "aws.lambda.log_group_name": "/aws/lambda/test",
                "aws.lambda.log_stream_name": "2019/4/1/[$LATEST]111a11a11111aa11",
                "aws.lambda.invocation.coldstart": True,
                "aws.lambda.invocation.timeout": False,
                "aws.lambda.invocation.request_id": "",
                "aws.lambda.invocation.memory_usage": 33
            },
            "applicationId": "111a11a11111aa11",
            "applicationDomainName": "API",
            "applicationClassName": "AWS-Lambda",
            "applicationName": "test",
            "applicationVersion": "$LATEST",
            "applicationStage": "",
            "applicationRuntime": "python",
            "applicationRuntimeVersion": "3",
            "applicationTags": {
            },
            "resources": [
                {
                    "resourceType": "HTTP",
                    "resourceName": "test.com",
                    "resourceOperation": "GET",
                    "resourceCount": 5,
                    "resourceErrorCount": 0,
                    "resourceDuration": 700,
                    "resourceErrors": [
                    ]
                }
            ]
        }
    }


@pytest.fixture
@mock.patch('catchpoint.reporter.requests')
def reporter(mock_requests):
    return Reporter('api key', mock_requests.Session())


@pytest.fixture
def catchpoint(reporter):
    catchpoint = Catchpoint(api_key="api_key", disable_metric=True)
    catchpoint.reporter = reporter
    return catchpoint


@pytest.fixture
def handler(catchpoint):
    @catchpoint.call
    def _handler(event, context):
        pass

    return catchpoint, _handler


@pytest.fixture
def handler_with_exception(catchpoint):
    @catchpoint.call
    def _handler(event, context):
        raise Exception('hello')

    return catchpoint, _handler


@pytest.fixture
def handler_with_user_error(catchpoint):
    @catchpoint.call
    def _handler(event, context):
        invocation_support.set_error(Exception("test"))

    return catchpoint, _handler


@pytest.fixture
def wrap_handler_with_catchpoint(catchpoint):
    def _wrap_handler_with_catchpoint(handler):
        return catchpoint, catchpoint(handler)

    return _wrap_handler_with_catchpoint


@pytest.fixture()
def mock_sqs_response():
    return {
        'MessageId': 'MessageID_1',
    }


@pytest.fixture()
def mock_sns_response():
    return {
        'MessageId': 'MessageID_1',
    }


@pytest.fixture()
def mock_kinesis_response():
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
    return response


@pytest.fixture()
def mock_firehose_response():
    response = {
        "ResponseMetadata":
            {
                "HTTPHeaders": {
                    "date": "Wed, 27 Mar 2019 14:00:00 GMT"
                }
            }
    }
    return response


@pytest.fixture()
def mock_s3_response():
    response = {
        "ResponseMetadata":
            {
                "HTTPHeaders": {
                    "x-amz-request-id": "C3D13FE58DE4C810"
                }
            }
    }
    return response


@pytest.fixture()
def mock_lambda_response():
    response = {
        "ResponseMetadata":
            {
                "HTTPHeaders": {
                    "x-amzn-requestid": "test-request-id"
                }
            }
    }
    return response


@pytest.fixture()
def mock_athena_start_query_exec_response():
    response = {
        "QueryExecutionId": "98765432-1111-1111-1111-12345678910"
    }
    return response


@pytest.fixture()
def mock_athena_list_query_executions_response():
    return {
        'QueryExecutionIds': [
            '98765432-1111-1111-1111-12345678910',
        ],
        'NextToken': 'string'
    }


@pytest.fixture()
def mock_athena_create_named_query_response():
    return {
        "NamedQueryId": "98765432-1111-1111-1111-12345678910"
    }


@pytest.fixture()
def mock_eventbridge_put_events_response():
    return {
        'FailedEntryCount': 0,
        'Entries': [
            {
                'EventId': 'test-event-id'
            }
        ]
    }


@pytest.fixture
def mock_dynamodb_event():
    event = {
        "Records": [
            {
                "eventID": "1",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "NewImage": {
                        "Message": {
                            "S": "New item!"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "SequenceNumber": "111",
                    "SizeBytes": 26,
                    "ApproximateCreationDateTime": 1480642020,
                },
                "awsRegion": "eu-west-2",
                "eventName": "INSERT",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            },
            {
                "eventID": "2",
                "eventVersion": "1.0",
                "dynamodb": {
                    "OldImage": {
                        "Message": {
                            "S": "New item!"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SequenceNumber": "222",
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SizeBytes": 59,
                    "NewImage": {
                        "Message": {
                            "S": "This item has changed"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "ApproximateCreationDateTime": 1480642020,

                },
                "awsRegion": "eu-west-2",
                "eventName": "MODIFY",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            }
        ]
    }
    return event


@pytest.fixture
def mock_dynamodb_delete_event():
    event = {
        "Records": [
            {
                "eventID": "1",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SizeBytes": 38,
                    "SequenceNumber": "333",
                    "OldImage": {
                        "Message": {
                            "S": "This item has changed"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "ApproximateCreationDateTime": 1480642020,

                },
                "awsRegion": "eu-west-2",
                "eventName": "REMOVE",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            }
        ]
    }
    return event


@pytest.fixture
def mock_dynamodb_event_trace_injected():
    event = {
        "Records": [
            {
                "eventID": "1",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "NewImage": {
                        "Message": {
                            "S": "New item!"
                        },
                        "Id": {
                            "N": "101"
                        },
                        constants.CATCHPOINT_SPAN_ID_KEY: {
                            "S": "test_id1"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "SequenceNumber": "111",
                    "SizeBytes": 26,
                    "ApproximateCreationDateTime": 1480642020,
                },
                "awsRegion": "eu-west-2",
                "eventName": "INSERT",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            },
            {
                "eventID": "2",
                "eventVersion": "1.0",
                "dynamodb": {
                    "OldImage": {
                        "Message": {
                            "S": "New item!"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SequenceNumber": "222",
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SizeBytes": 59,
                    "NewImage": {
                        "Message": {
                            "S": "This item has changed"
                        },
                        "Id": {
                            "N": "101"
                        },
                        constants.CATCHPOINT_SPAN_ID_KEY: {
                            "S": "test_id2"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "ApproximateCreationDateTime": 1480642020,

                },
                "awsRegion": "eu-west-2",
                "eventName": "MODIFY",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            },
            {
                "eventID": "3",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "SizeBytes": 38,
                    "SequenceNumber": "333",
                    "OldImage": {
                        "Message": {
                            "S": "This item has changed!"
                        },
                        "Id": {
                            "N": "101"
                        },
                        constants.CATCHPOINT_SPAN_ID_KEY: {
                            "S": "test_id3"
                        }
                    },
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                    "ApproximateCreationDateTime": 1480642020,

                },
                "awsRegion": "eu-west-2",
                "eventName": "REMOVE",
                "eventSourceARN": "arn:aws:dynamodb:eu-west-2:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899",
                "eventSource": "aws:dynamodb"
            }
        ]
    }
    return event


@pytest.fixture
def mock_sqs_event():
    event = {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": "Hello from SQS!",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:eu-west-2:123456789012:MyQueue",
                "awsRegion": "eu-west-2"
            }
        ]
    }
    return event


@pytest.fixture
def mock_sns_event():
    event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:eu-west-2:{{accountId}}:ExampleTopic",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                    "TopicArn": "arn:aws:sns:eu-west-2:123456789012:ExampleTopic",
                    "Subject": "example subject",
                    "Message": "example message",
                    "Timestamp": "1970-01-01T00:00:00.000Z",
                    "SignatureVersion": "1",
                    "Signature": "EXAMPLE",
                    "SigningCertUrl": "EXAMPLE",
                    "UnsubscribeUrl": "EXAMPLE",
                    "MessageAttributes": {
                        "Test": {
                            "Type": "String",
                            "Value": "TestString"
                        },
                        "TestBinary": {
                            "Type": "Binary",
                            "Value": "TestBinary"
                        }
                    }
                }
            }
        ]
    }
    return event


@pytest.fixture
def mock_kinesis_event():
    event = {
        "Records": [
            {
                "kinesis": {
                    "partitionKey": "partitionKey-03",
                    "kinesisSchemaVersion": "1.0",
                    "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=",
                    "sequenceNumber": "49545115243490985018280067714973144582180062593244200961",
                    "approximateArrivalTimestamp": 1428537600
                },
                "eventSource": "aws:kinesis",
                "eventID": "shardId-000000000000:49545115243490985018280067714973144582180062593244200961",
                "invokeIdentityArn": "arn:aws:iam::EXAMPLE",
                "eventVersion": "1.0",
                "eventName": "aws:kinesis:record",
                "eventSourceARN": "arn:aws:kinesis:eu-west-2:123456789012:stream/example_stream",
                "awsRegion": "eu-west-2"
            }
        ]
    }
    return event


@pytest.fixture
def mock_cloudwatch_schedule_event():
    event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "{{account-id}}",
        "time": "1970-01-01T00:00:00Z",
        "region": "eu-west-2",
        "resources": [
            "arn:aws:events:eu-west-2:123456789012:rule/ExampleRule"
        ],
        "detail": {}
    }
    return event


@pytest.fixture
def mock_cloudwatch_logs_event():
    event = {
        "awslogs": {
            "data": "H4sIAAAAAAAAAHWPwQqCQBCGX0Xm7EFtK+smZBEUgXoLCdMhFtKV3akI8d0bLYmibvPPN3wz00CJxmQnTO41whwWQRIctmEcB6sQbFC3CjW3XW8kxpOpP+OC22d1Wml1qZkQGtoMsScxaczKN3plG8zlaHIta5KqWsozoTYw3/djzwhpLwivWFGHGpAFe7DL68JlBUk+l7KSN7tCOEJ4M3/qOI49vMHj+zCKdlFqLaU2ZHV2a4Ct/an0/ivdX8oYc1UVX860fQDQiMdxRQEAAA=="
        }
    }
    return event


@pytest.fixture
def mock_cloudfront_event():
    # Modify Response Header
    event = {
        "Records": [
            {
                "cf": {
                    "config": {
                        "distributionId": "EXAMPLE"
                    },
                    "request": {
                        "uri": "/test",
                        "method": "GET",
                        "clientIp": "2001:cdba::3257:9652",
                        "headers": {
                            "user-agent": [
                                {
                                    "key": "User-Agent",
                                    "value": "Test Agent"
                                }
                            ],
                            "host": [
                                {
                                    "key": "Host",
                                    "value": "d123.cf.net"
                                }
                            ],
                            "cookie": [
                                {
                                    "key": "Cookie",
                                    "value": "SomeCookie=1; AnotherOne=A; X-Experiment-Name=B"
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }
    return event


@pytest.fixture
def mock_firehose_event():
    event = {
        "invocationId": "invocationIdExample",
        "deliveryStreamArn": "arn:aws:kinesis:EXAMPLE/exampleStream",
        "region": "eu-west-2",
        "records": [
            {
                "recordId": "49546986683135544286507457936321625675700192471156785154",
                "approximateArrivalTimestamp": 1495072949453,
                "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4="
            }
        ]
    }
    return event


@pytest.fixture
def mock_apigateway_proxy_event():
    event = {
        "body": "eyJ0ZXN0IjoiYm9keSJ9",
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "queryStringParameters": {
            "foo": "bar"
        },
        "pathParameters": {
            "proxy": "/path/to/resource"
        },
        "stageVariables": {
            "baz": "qux"
        },
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "1234567890.execute-api.eu-west-2.amazonaws.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Custom User Agent String",
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "123456",
            "stage": "prod",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "requestTime": "09/Apr/2015:12:34:56 +0000",
            "requestTimeEpoch": 1428582896000,
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "accessKey": None,
                "sourceIp": "127.0.0.1",
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Custom User Agent String",
                "user": None
            },
            "path": "/prod/path/to/resource",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "apiId": "1234567890",
            "protocol": "HTTP/1.1"
        }
    }
    return event


@pytest.fixture
def mock_apigateway_event():
    event = {
        'body-json': {},
        'params': {
            'path': {},
            'querystring': {},
            'header': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'br, gzip, deflate',
                'Accept-Language': 'tr-tr',
                'CloudFront-Forwarded-Proto': 'https',
                'CloudFront-Is-Desktop-Viewer': 'true',
                'CloudFront-Is-Mobile-Viewer': 'false',
                'CloudFront-Is-SmartTV-Viewer': 'false',
                'CloudFront-Is-Tablet-Viewer': 'false',
                'CloudFront-Viewer-Country': 'TR',
                'Host': 'random.execute-api.us-west-2.amazonaws.com',
                'User-Agent': 'Mozilla/5.0 ',
                'Via': '2.0 7c2d73d3cd46e357090188fa2946f746.cloudfront.net (CloudFront)',
                'X-Amz-Cf-Id': '2oERVyfE28F7rylVV0ZOdEBnmogTSblZNOrSON_vGJFBweD1tIM-dg==',
                'X-Amzn-Trace-Id': 'Root=1-5c3d8b9e-794ee8faf33ffce551c0146b',
                'X-Forwarded-Port': '443',
                'X-Forwarded-Proto': 'https'
            }
        },
        'stage-variables': {},
        'context': {
            'account-id': '',
            'api-id': 'random',
            'api-key': '',
            'authorizer-principal-id': '',
            'caller': '',
            'cognito-authentication-provider': '',
            'cognito-authentication-type': '',
            'cognito-identity-id': '',
            'cognito-identity-pool-id': '',
            'http-method': 'GET',
            'stage': 'dev',
            'source-ip': '',
            'user': '',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14)',
            'user-arn': '',
            'request-id': '27eca8d1-1897-11e9-9eed-0d1fbe8bcba6',
            'resource-id': '3ggrja',
            'resource-path': '/hello'
        }
    }
    return event


@pytest.fixture
def mock_s3_event():
    event = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "eu-west-2",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": "example-bucket",
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:aws:s3:::example-bucket"
                    },
                    "object": {
                        "key": "test/key",
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }
    return event


@pytest.fixture
def mock_eventbridge_event():
    event = {
        "version": "0",
        "id": "51c0891d-0e34-45b1-83d6-95db273d1602",
        "detail-type": "EC2 Command Status-change Notification",
        "source": "aws.ssm",
        "account": "123456789012",
        "time": "2020-03-10T21:51:32Z",
        "region": "eu-west-2",
        "resources": ["arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"],
        "detail": {
            "command-id": "e8d3c0e4-71f7-4491-898f-c9b35bee5f3b",
            "document-name": "AWS-RunPowerShellScript",
            "expire-after": "2020-03-14T22:01:30.049Z",
            "parameters": {
                "executionTimeout": ["3600"],
                "commands": ["date"]
            },
            "requested-date-time": "2020-03-10T21:51:30.049Z",
            "status": "Success"
        }
    }
    return event


@pytest.fixture(scope='session', autouse=True)
def mock_context_clear():
    with mock.patch('catchpoint.context.execution_context_manager.ExecutionContextManager.clear') as _fixture:
        yield _fixture
