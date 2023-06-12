import mock
import requests

from catchpoint import constants
from catchpoint.compat import urlparse
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer


def test_successful_http_call():
    try:
        url = 'https://jsonplaceholder.typicode.com/users'
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise
    finally:
        tracer.clear()


def test_http_put():
    try:
        url = 'https://jsonplaceholder.typicode.com/users/3'
        parsed_url = urlparse(url)
        path = parsed_url.path
        normalized_path = "/users"
        query = parsed_url.query
        host = parsed_url.netloc

        requests.put(url, data={"message": "test"})
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
        assert http_span.get_tag(constants.HttpTags['BODY']) == "message=test"
    except Exception:
        raise
    finally:
        tracer.clear()


def test_http_put_body_masked():
    try:
        ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_BODY_MASK, 'true')
        url = 'https://jsonplaceholder.typicode.com/users/3'
        parsed_url = urlparse(url)
        path = parsed_url.path
        normalized_path = "/users"
        query = parsed_url.query
        host = parsed_url.netloc

        requests.put(url, data={"message": "test"})
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
        assert http_span.get_tag(constants.HttpTags['BODY']) is None
    except Exception:
        raise
    finally:
        tracer.clear()


def test_successful_http_call_with_query_params():
    try:
        url = "https://jsonplaceholder.typicode.com/users/1?test=test"
        parsed_url = urlparse(url)
        path = parsed_url.path
        normalized_path = "/users"
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise


def test_http_call_with_session():
    try:
        url = 'https://httpbin.org/cookies/set/sessioncookie/123456789'
        parsed_url = urlparse(url)
        query = parsed_url.query
        host = parsed_url.netloc

        s = requests.Session()
        s.get(url)

        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise


def test_erroneous_http_call():
    try:
        url = 'http://adummyurlthatnotexists.xyz/'
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        try:
            requests.get(url)
        except Exception:
            pass

        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
        assert http_span.get_tag('error') == True
    except Exception:
        raise
    finally:
        tracer.clear()


def test_http_path_depth():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH, '2')
    try:
        url = 'https://jsonplaceholder.typicode.com/asd/qwe/xyz'
        parsed_url = urlparse(url)
        normalized_path = "/asd/qwe"
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise


@mock.patch('catchpoint.integrations.requests.RequestsIntegration.actual_call')
def test_apigw_call(mock_actual_call):
    mock_actual_call.return_value = requests.Response()
    mock_actual_call.return_value.headers = {"x-amz-apigw-id": "test_id"}
    try:
        url = 'https://1a23bcdefg.execute-api.us-west-2.amazonaws.com/dev/test'
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc
        normalized_path = "/dev"

        requests.get(url)
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['APIGATEWAY']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise


@mock.patch('catchpoint.integrations.requests.RequestsIntegration.actual_call')
def test_apigw_call_v2(mock_actual_call):
    mock_actual_call.return_value = requests.Response()
    mock_actual_call.return_value.headers = {"apigw-requestid": "test_id", constants.TRIGGER_RESOURCE_NAME_KEY: "test"}
    try:
        url = 'https://1a23bcdefg.execute-api.us-west-2.amazonaws.com/dev/test'
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = CatchpointTracer.get_instance()
        http_span = tracer.get_spans()[1]

        assert http_span.operation_name == "test"
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['APIGATEWAY']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise


@mock.patch('catchpoint.integrations.requests.RequestsIntegration.actual_call')
def test_http_4xx_error(mock_actual_call):
    mock_actual_call.return_value = requests.Response()
    mock_actual_call.return_value.status_code = 404
    mock_actual_call.return_value.reason = "Not Found"

    url = 'http://adummyurlthatnotexists.xyz/'
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query
    host = parsed_url.netloc

    requests.get(url)

    tracer = CatchpointTracer.get_instance()
    http_span = tracer.get_spans()[1]

    assert http_span.operation_name == host + path
    assert http_span.domain_name == constants.DomainNames['API']
    assert http_span.class_name == constants.ClassNames['HTTP']

    assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
    assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
    assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
    assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    assert http_span.get_tag('error') == True
    assert http_span.get_tag('error.kind') == 'HttpError'
    assert http_span.get_tag('error.message') == 'Not Found'


@mock.patch('catchpoint.integrations.requests.RequestsIntegration.actual_call')
def test_http_4xx_error_with_min_status_500(mock_actual_call, monkeypatch):
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN, '500')
    mock_actual_call.return_value = requests.Response()
    mock_actual_call.return_value.status_code = 404
    mock_actual_call.return_value.reason = "Not Found"

    url = 'http://adummyurlthatnotexists.xyz/'
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query
    host = parsed_url.netloc

    requests.get(url)

    tracer = CatchpointTracer.get_instance()
    http_span = tracer.get_spans()[1]

    assert http_span.operation_name == host + path
    assert http_span.domain_name == constants.DomainNames['API']
    assert http_span.class_name == constants.ClassNames['HTTP']

    assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
    assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
    assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
    assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    assert http_span.get_tag('error') is None
    assert http_span.get_tag('error.kind') is None
    assert http_span.get_tag('error.message') is None


@mock.patch('catchpoint.integrations.requests.RequestsIntegration.actual_call')
def test_http_5xx_error(mock_actual_call):
    mock_actual_call.return_value = requests.Response()
    mock_actual_call.return_value.status_code = 500
    mock_actual_call.return_value.reason = "Internal Server Error"

    url = 'http://adummyurlthatnotexists.xyz/'
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query
    host = parsed_url.netloc

    requests.get(url)

    tracer = CatchpointTracer.get_instance()
    http_span = tracer.get_spans()[1]

    assert http_span.operation_name == host + path
    assert http_span.domain_name == constants.DomainNames['API']
    assert http_span.class_name == constants.ClassNames['HTTP']

    assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
    assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
    assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
    assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    assert http_span.get_tag('error') is True
    assert http_span.get_tag('error.kind') == 'HttpError'
    assert http_span.get_tag('error.message') == 'Internal Server Error'
