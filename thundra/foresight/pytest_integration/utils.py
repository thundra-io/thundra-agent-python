from thundra.foresight.pytest_integration.pytest_helper import PytestHelper
from thundra.foresight.test_status import increase_actions, TestStatus
import thundra.foresight.pytest_integration.constants as constants
import traceback
import wrapt



def check_test_case_result(item, execution_context, result, exception):
    test_status = TestStatus.SUCCESSFUL
    xfail = hasattr(result, "wasxfail") or "xfail" in result.keywords
    has_skip_keyword = any(x in result.keywords for x in ["skip", "skipif"])

    if hasattr(item, constants.THUNDRA_MARKED_AS_SKIPPED):
        delattr(item, constants.THUNDRA_MARKED_AS_SKIPPED)
        test_status = TestStatus.SKIPPED
    elif (exception and hasattr(exception.value, "msg") and 
        "timeout" in exception.value.msg.lower()):
        test_status = TestStatus.ABORTED
        handle_error(exception, result, execution_context)
        execution_context.timeout = True
    elif result.skipped:
        if xfail and not has_skip_keyword:
            test_status = TestStatus.SUCCESSFUL
        else:
            test_status = TestStatus.SKIPPED
    elif result.passed:
        test_status = TestStatus.SUCCESSFUL
    else: # failed
        test_status = TestStatus.FAILED
        handle_error(exception, result, execution_context)
    return test_status


def handle_test_status(item, test_status, execution_context):
    increase_action = increase_actions[test_status]
    execution_context.set_status(test_status)
    if increase_action:
        setattr(item, constants.THUNDRA_TEST_RESULTED, True)
        increase_action()


def handle_error(exception, result, execution_context):
    execution_context.error = {
                    'type': type(exception).__name__,
                    'message': result.longreprtext,
                    'traceback': ''.join(traceback.format_tb(exception.tb))
                }


def set_attributes_test_item(item):
    setattr(item, "scope", "function")  
    setattr(item.parent, "scope", "module")
    own_markers = item.own_markers
    check_marked_as_skipped = any("skip" in mark.name for mark in own_markers)
    if check_marked_as_skipped:
        setattr(item, constants.THUNDRA_MARKED_AS_SKIPPED, True)


def check_test_status_state(item, call):
    is_setup_or_teardown = call.when == 'setup' or call.when == 'teardown'
    exception = call.excinfo
    status = True
    if (is_setup_or_teardown and not exception) or hasattr(item, constants.THUNDRA_TEST_RESULTED):
        status = False
    return status, exception


def _wrapper_setup_fixture(wrapped, instance, args, kwargs):
    res = None
    try:
        request = args[1]
        if not "x_thundra" in request.fixturename:
            if request.scope == "function":
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