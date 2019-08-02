import os
import mock
import requests
from thundra.opentracing.tracer import ThundraTracer

from thundra.compat import urlparse

from thundra import constants


def test_successful_http_call():
    try:
        url = 'https://jsonplaceholder.typicode.com/users'
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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


def test_http_put_body_masked(monkeypatch):
    try:
        monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_HTTP_BODY, 'true')
        url = 'https://jsonplaceholder.typicode.com/users/3'
        parsed_url = urlparse(url)
        path = parsed_url.path
        normalized_path = "/users"
        query = parsed_url.query
        host = parsed_url.netloc

        requests.put(url, data={"message": "test"})
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

        assert http_span.operation_name == host + normalized_path
        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'PUT'
        assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == host + path
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
        assert http_span.get_tag(constants.HttpTags['BODY']) == None
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
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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
    finally:
        tracer.clear()


def test_http_call_with_session():
    try:
        url = 'https://httpbin.org/cookies/set/sessioncookie/123456789'
        parsed_url = urlparse(url)
        query = parsed_url.query
        host = parsed_url.netloc

        s = requests.Session()
        s.get(url)

        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

        assert http_span.domain_name == constants.DomainNames['API']
        assert http_span.class_name == constants.ClassNames['HTTP']

        assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
        assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
        assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    except Exception:
        raise
    finally:
        tracer.clear()


def test_errorneous_http_call():
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

        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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


def test_http_path_depth(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_AGENT_TRACE_INTEGRATTIONS_HTTP_URL_DEPTH, "2")
    try:
        url = 'https://jsonplaceholder.typicode.com/asd/qwe/xyz'
        parsed_url = urlparse(url)
        normalized_path = "/asd/qwe"
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc

        requests.get(url)
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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
    finally:
        tracer.clear()


@mock.patch('thundra.integrations.requests.RequestsIntegration.actual_call')
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
        tracer = ThundraTracer.get_instance()
        http_span = tracer.get_spans()[0]

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
    finally:
        tracer.clear()
