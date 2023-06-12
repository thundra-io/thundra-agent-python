from catchpoint.context.execution_context_manager import ExecutionContextManager


def test_invocation_support_error_set_to_root_span(handler_with_user_error, mock_context, mock_event):
    _, handler = handler_with_user_error

    handler(mock_event, mock_context)
    execution_context = ExecutionContextManager.get()

    assert execution_context.root_span.get_tag('error') is True
    assert execution_context.root_span.get_tag('error.kind') == 'Exception'
    assert execution_context.root_span.get_tag('error.message') == 'test'
