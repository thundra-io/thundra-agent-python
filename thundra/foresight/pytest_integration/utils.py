import wrapt
from thundra.foresight.pytest_integration.pytest_helper import PytestHelper, HandleSpan
import traceback

"""
    Refactor this file. It's been written rapidly.
"""

class TestTraceConstants:
    THUNDRA_MARKED_AS_SKIPPED = "thundra_marked_as_skipped"
    THUNDRA_TEST_ALREADY_FINISHED = "thundra_test_already_finished"
    THUNDRA_TEST_STARTED = "thundra_test_started"
    THUNDRA_TEST_RESULTED = "thundra_test_resulted"

def handle_fixture_error(request, error):
    scope = HandleSpan.extract_scope(request)
    span = scope.span
    span.set_error_to_tag(error)

    
def _wrapper_setup_fixture(wrapped, instance, args, kwargs):
    res = None
    try:
        request = args[1]
        if not "x_thundra" in request.fixturename:
            if request.scope == "function":
                if not hasattr(request.node, TestTraceConstants.THUNDRA_TEST_STARTED):
                    setattr(request.node, TestTraceConstants.THUNDRA_TEST_STARTED, True)
                    PytestHelper.start_test_span(request.node)
                PytestHelper.start_before_each_span(request)
            else:
                PytestHelper.start_before_all_span(request)
            res = wrapped(*args, **kwargs)
            if request.scope == "function":
                PytestHelper.finish_before_each_span(request)
            else:
                PytestHelper.finish_before_all_span(request)
        else:
            res = wrapped(*args, **kwargs)
    except Exception as err:
        print("error occured while fixture_setup function wrapped", err) # TODO
    if res:
        return res



def _wrapper_teardown_fixture(wrapped, instance, args, kwargs):
    try:
        if not "x_thundra" in kwargs["request"].fixturename:
            request = kwargs["request"]
            if request.scope == "function":
                PytestHelper.start_after_each_span(request)
            else:
                PytestHelper.start_after_all_span(request)
            wrapped(*args, **kwargs)
            if request.scope == "function":
                PytestHelper.finish_after_each_span(request)
            else:
                PytestHelper.finish_after_all_span(request)
        else:
            wrapped(*args, **kwargs)
    except Exception as err:
        print("error occured while fixture_teardown function wrapped", err) # TODO


def patch():
    '''
        fixture function has been called in call_fixture_func.
    '''
    wrapt.wrap_function_wrapper(
            "_pytest.fixtures",
            "call_fixture_func",
            _wrapper_setup_fixture
        )
    '''
        teardown functions has been stored in a stack(FixtureDef._finalizer).
        finish function has been iterated over this stack and call teardown fixtures.
    '''    
    wrapt.wrap_function_wrapper(
            "_pytest.fixtures",
            "FixtureDef.finish",
            _wrapper_teardown_fixture
        )


def unpatch():
    pass #TODO


def handle_error(exception, result, execution_context):
    execution_context.error = {
                    'type': type(exception).__name__,
                    'message': result.longreprtext,
                    'traceback': ''.join(traceback.format_tb(exception.tb))
                }