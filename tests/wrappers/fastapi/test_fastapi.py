from catchpoint import constants
from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.wrappers.fastapi.fastapi_wrapper import FastapiWrapper
from catchpoint.context.tracing_execution_context_provider import TracingExecutionContextProvider
from catchpoint.wrappers import wrapper_utils


def test_fastapi_hooks_called(test_app, monkeypatch):
    
    def mock_before_request(self, request, req_body):
        ExecutionContextManager.set_provider(TracingExecutionContextProvider())
        execution_context = wrapper_utils.create_execution_context()
        execution_context.platform_data["request"] = request
        execution_context.platform_data["request"]["body"] = req_body

        self.plugin_context.request_count += 1
        self.execute_hook("before:invocation", execution_context)

        assert execution_context.root_span.operation_name == '/1'
        assert execution_context.root_span.get_tag('http.method') == 'GET'
        assert execution_context.root_span.get_tag('http.host') == 'testserver'
        assert execution_context.root_span.get_tag('http.query_params') == b''
        assert execution_context.root_span.get_tag('http.path') == '/1'
        assert execution_context.root_span.class_name == constants.ClassNames['FASTAPI']
        assert execution_context.root_span.domain_name == 'API'

        return execution_context

    def mock_after_request(self, execution_context):
        assert execution_context.response.body == b'{"hello_world":1}'
        assert execution_context.response.status_code == 200
        self.prepare_and_send_reports_async(execution_context)
        ExecutionContextManager.clear()

    monkeypatch.setattr(FastapiWrapper, "before_request", mock_before_request)
    monkeypatch.setattr(FastapiWrapper, "after_request", mock_after_request)
    response = test_app.get('/1')

def test_fastapi_errornous(test_app, monkeypatch):
    try:

        def mock_error_handler(self, error):
            execution_context = ExecutionContextManager.get()
            if error:
                execution_context.error = error

            self.prepare_and_send_reports_async(execution_context)
            assert error.type == "RuntimeError"
            assert error.message == "Test Error"

        monkeypatch.setattr(FastapiWrapper, "error_handler", mock_error_handler)

        test_app.get('/error')
    except:
        "Error thrown in endpoint"