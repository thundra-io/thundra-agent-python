import requests
from thundra.opentracing.tracer import ThundraTracer
from urllib.parse import urlparse
from thundra import constants

def test_successful_http_call():
    url = 'https://jsonplaceholder.typicode.com/users/3'
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query
    host = parsed_url.netloc
    
    requests.get(url)
    tracer = ThundraTracer.get_instance()
    http_span = tracer.recorder.finished_span_stack[0]

    assert http_span.operation_name == url
    assert http_span.domain_name == constants.DomainNames['API']
    assert http_span.class_name == constants.ClassNames['HTTP']

    assert http_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['HTTP']
    assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'CALL'
    assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == url
    assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
    assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
    assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query

    tracer.clear()

def test_errorneous_http_call():
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
    http_span = tracer.recorder.finished_span_stack[0]

    assert http_span.operation_name == url
    assert http_span.domain_name == constants.DomainNames['API']
    assert http_span.class_name == constants.ClassNames['HTTP']

    assert http_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['HTTP']
    assert http_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'CALL'
    assert http_span.get_tag(constants.HttpTags['HTTP_METHOD']) == 'GET'
    assert http_span.get_tag(constants.HttpTags['HTTP_URL']) == url
    assert http_span.get_tag(constants.HttpTags['HTTP_HOST']) == host
    assert http_span.get_tag(constants.HttpTags['HTTP_PATH']) == path
    assert http_span.get_tag(constants.HttpTags['QUERY_PARAMS']) == query
    assert http_span.get_tag('error') == True

    tracer.clear()
    
    
