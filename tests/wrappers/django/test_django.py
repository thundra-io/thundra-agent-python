from unittest import mock
from unittest.mock import Mock

from django.test import Client
from django.test import RequestFactory

from tests.wrappers.django.app.views import index
from catchpoint import constants
from catchpoint.wrappers.django.django_wrapper import DjangoWrapper

c = Client()


@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.process_exception')
@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.after_request')
@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.before_request')
def test_django_middleware_wrapper_calls(mock_before_request, mock_after_request, mock_process_exception):
    response = c.get('/')

    assert response.status_code == 200
    assert response.content == b"Test!"
    assert mock_before_request.called
    assert mock_after_request.called
    assert not mock_process_exception.called


@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.process_exception')
@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.after_request')
@mock.patch('catchpoint.wrappers.django.django_wrapper.DjangoWrapper.before_request')
def test_erroneous_view(mock_before_request, mock_after_request, mock_process_exception):
    try:
        c.get('/error/')
    except:
        "Error thrown in view"

    assert mock_before_request.called
    assert mock_after_request.called
    assert mock_process_exception.called


def test_wrapper():
    wrapper = DjangoWrapper()
    wrapper.reporter = Mock()
    factory = RequestFactory()
    request = factory.get('/', {'bar': 'baz'})
    execution_context = wrapper.before_request(request)
    assert execution_context.root_span.operation_name == '/'
    assert execution_context.root_span.get_tag('http.method') == 'GET'
    assert execution_context.root_span.get_tag('http.host') == 'testserver'
    assert execution_context.root_span.get_tag('http.query_params').get('bar') == 'baz'
    assert execution_context.root_span.get_tag('http.path') == '/'
    assert execution_context.root_span.class_name == constants.ClassNames['DJANGO']
    assert execution_context.root_span.domain_name == 'API'

    assert execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['testserver/']
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'HTTP'

    response = index(request)

    wrapper.after_request(response)

    assert execution_context.response == response
    assert execution_context.invocation_data['applicationId'] == 'python:Django:eu-west-1:test'

