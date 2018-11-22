import pytest
import mock

from thundra.thundra_agent import Thundra
from thundra.reporter import Reporter
import boto3


class MockContext:

    def __init__(self, f_name='test_func'):
        self.memory_limit_in_mb = '128'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name[]id'
        self.aws_request_id = 'aws_request_id'
        self.invoked_function_arn = 'invoked_function_arn'
        self.function_version = 'function_version'
        self.function_name = f_name


@pytest.fixture
@mock.patch('thundra.reporter.requests')
def reporter(mock_requests):
    return Reporter('api key', mock_requests.Session())


@pytest.fixture
def thundra(reporter):
    thundra = Thundra('api-key', disable_metric=True)
    thundra.reporter = reporter
    return thundra


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def mock_event():
    event = {
        'message': 'Hello'
    }
    return event


@pytest.fixture
def dynamodb_handler(thundra):
    @thundra.call
    def _handler(event, context):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-table')

        response = table.get_item(
            Key={
                'username': 'janedoe',
                'last_name': 'Doe'
            }
        )
        return response
    # open("results.json", "w").write(str(vars(thundra)))
    return thundra, _handler