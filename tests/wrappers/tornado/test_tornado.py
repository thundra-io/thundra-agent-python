from tornado.testing import AsyncHTTPTestCase
from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint import constants
from unittest import mock
from tornado.httputil import url_concat


import tests.wrappers.tornado.hello as hello


class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        return hello.make_app()

    @mock.patch('catchpoint.wrappers.tornado.tornado_wrapper.TornadoWrapper.after_request')
    @mock.patch('catchpoint.wrappers.tornado.tornado_wrapper.TornadoWrapper.before_request')
    def test_homepage(self, mock_before_request, mock_after_request):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'Hello, world')
        assert mock_before_request.called
        assert mock_after_request.called

    @mock.patch('catchpoint.wrappers.web_wrapper_utils.finish_trace')
    def test_successful_view(self, finish_trace):
        query_string={'foo': 'baz'}
        response = self.fetch(url_concat("/query", query_string))
        execution_context = ExecutionContextManager.get()
        self.assertEqual(execution_context.root_span.operation_name, '/query')
        self.assertEqual(execution_context.root_span.get_tag('http.method'), 'GET')
        self.assertEqual(execution_context.root_span.get_tag('http.host'), '127.0.0.1')
        self.assertEqual(execution_context.root_span.get_tag('http.query_params'), 'foo=baz')
        self.assertEqual(execution_context.root_span.get_tag('http.path'), '/query')
        self.assertEqual(execution_context.root_span.class_name, constants.ClassNames['TORNADO'])
        self.assertEqual(execution_context.root_span.domain_name, 'API')
        self.assertEqual(execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']), ['127.0.0.1/query'])
        self.assertEqual(execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']), 'API')
        self.assertEqual(execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']), 'HTTP')
        self.assertEqual(execution_context.response.status_code, 200)
        self.assertEqual(response.body, b'baz')
        ExecutionContextManager.clear()
