from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from unittest import mock
from unittest.mock import Mock
from fastapi.testclient import TestClient

from thundra import constants
from thundra.context.execution_context_manager import ExecutionContextManager

from thundra.wrappers.fastapi.fastapi_wrapper import FastapiWrapper

app = FastAPI()

client = TestClient(app)

@app.get("/")
def root():
    return JSONResponse({ "hello": "world"})


def read_request(request: Request):
    return JSONResponse({"content": "request gathered!!!"})

@app.route("/error")
def error():
    raise RuntimeError("Test")


@mock.patch('thundra.wrappers.fastapi.fastapi_wrapper.FastapiWrapper.before_request')
@mock.patch('thundra.wrappers.fastapi.fastapi_wrapper.FastapiWrapper.after_request')
def test_fastapi_hooks_called(mock_before_request, mock_after_request):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'hello':"world"}

    assert mock_before_request.called
    assert mock_after_request.called


@mock.patch('thundra.wrappers.fastapi.fastapi_wrapper.FastapiWrapper.before_request')
@mock.patch('thundra.wrappers.fastapi.fastapi_wrapper.FastapiWrapper.error_handler')
def test_fastapi_errornous(mock_before_request, mock_error_handler):
    try:
        client.get('/error/')
    except:
        "Error thrown in endpoint"

    assert mock_before_request.called
    assert mock_error_handler.called


def test_successful_view():
    from starlette.requests import Request
    scope = {
        'method': 'GET',
        'type': 'http',
        'headers': [[b'host', b'asgi-scope.now.sh'],
             [b'x-now-id', b'fb6gw-1527863960919-mjYC9OJ9WTsfnw4EiRTDmMst'],
             [b'x-now-log-id', b'mjYC9OJ9WTsfnw4EiRTDmMst'],
             [b'connection', b'close'],
             [b'user-agent',
              b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko'
              b'/20100101 Firefox/60.0'],
             [b'accept',
              b'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q='
              b'0.8'],
             [b'accept-language', b'en-US,en;q=0.5'],
             [b'accept-encoding', b'gzip, deflate, br'],
             [b'upgrade-insecure-requests', b'1']],
        'path': '/',
        'query_string': b'param=1',
        'server': ('localhost', 8000)
    }
    request = Request(scope)
    wrapper = FastapiWrapper()
    wrapper.reporter = "fastapi_test"
    execution_context = wrapper.before_request(scope, None)

    assert execution_context.root_span.operation_name == '/'
    assert execution_context.root_span.get_tag('http.method') == 'GET'
    assert execution_context.root_span.get_tag('http.host') == 'localhost'
    assert execution_context.root_span.get_tag('http.query_params') == b'param=1'
    assert execution_context.root_span.get_tag('http.path') == '/'
    assert execution_context.root_span.class_name == constants.ClassNames['FASTAPI']
    assert execution_context.root_span.domain_name == 'API'

    assert execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['localhost/']
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'HTTP'

    response = read_request(request)
    execution_context.response = response
    wrapper.after_request(execution_context)

    assert execution_context.response == response
    assert execution_context.response.status_code == 200
    ExecutionContextManager.clear()