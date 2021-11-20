from foresight.pytest_integration.pytest_helper import PytestHelper
from foresight.test_status import increase_actions, TestStatus
import foresight.pytest_integration.constants as constants
import wrapt, logging, traceback


logger = logging.getLogger(__name__)

class XPassedException(Exception):
    pass


def check_test_case_result(item, execution_context, result, exception):
    """ Handle test case result.

    Args:
        item (pytest.Item): Current running test case.
        execution_context (TestCaseExecutionContext): Thundra execution context
        result (pytest.Result): test case result
        exception (pytest.ExceptionInfo): ExceptionInfo for test case if any. 

    Returns:
        str: One of the result in TestStatus class.
    """
    test_status = TestStatus.SKIPPED
    try:
        xfail = (hasattr(result, "wasxfail") or "xfail" in result.keywords) and check_and_get_xfail_condition(item)
        has_skip_keyword = any(x in result.keywords for x in ["skip", "skipif", "skipped"])

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
            if xfail and not has_skip_keyword:
                if exception == None:
                    exception = XPassedException(f"{result.nodeid} test result has been passed while expecting to get xfail!")
                test_status = TestStatus.FAILED
                handle_xpass(exception, result, execution_context)
            else:
                test_status = TestStatus.SUCCESSFUL
        else: # failed
            test_status = TestStatus.FAILED
            handle_error(exception, result, execution_context)
    except Exception as err:
        logger.error("Couldn't set test status properly for pytest: {}".format(err))
        pass
    return test_status

def check_and_get_xfail_condition(item):
    """Check test item that marked as xfail and get its xfail condition if it exists.

    Args:
        item (pytest.Item): Test case item that contains all info about current test.

    Returns:
        bool: If condition is string, then first evaluate and return result. If condition is bool, return
            immediately the bool. If there is an exception, always returns True.
    """
    try:
        own_markers = item.own_markers
        for i in own_markers:
            if i.name == "xfail" and len(i.args) > 0:
                condition_xfail = i.args[0]
                if isinstance(condition_xfail, str):
                    from argparse import Namespace
                    import os, sys
                    result = eval(condition_xfail, Namespace(globals=globals(), os=os, sys=sys, config=item.config).__dict__)
                    return result
                elif isinstance(condition_xfail, bool):
                    if condition_xfail == False:
                        return False
                    else:
                        return True
                else:
                    break
    except Exception as e:
        logger.error("Check and get xfail condition error: {}".format(e))
        pass
    return True


def update_test_status(item, test_status, execution_context):
    """update successful, skipped, aborted and total test status  w.r.t test case result calculated in 
    check_test_case_result function.

    Args:
        item (pytest.Item): Current running test case
        test_status (str): Current test case result
        execution_context (TestCaseExecutionContext): Execution context for test case
    """
    try:
        increase_action = increase_actions[test_status]
        execution_context.set_status(test_status)
        if increase_action:
            setattr(item, constants.THUNDRA_TEST_RESULTED, True)
            increase_action()
    except Exception as err:
        logger.error("Couldn't update test status for pytest: {}".format(err))
        pass


def handle_xpass(exception, result, execution_context):
    """Set exception into execution context if any.

    Args:
        exception (pytest.ExceptionInfo): Test case Exception info
        result (pytest.Result): Test result 
        execution_context (TestCaseExecutionContext): Execution context for test case
    """
    try:
        execution_context.error = {
                        'type': type(exception).__name__,
                        'message': result.longreprtext or str(exception), # TODO longreprtext can be empty. Search what can be used for it.
                        'traceback': ''
                    }
    except Exception as err:
        logger.error("Couldn't handle error for pytest: {}".format(err))
        pass

def handle_error(exception, result, execution_context):
    """Set exception into execution context if any.

    Args:
        exception (pytest.ExceptionInfo): Test case Exception info
        result (pytest.Result): Test result 
        execution_context (TestCaseExecutionContext): Execution context for test case
    """
    try:
        execution_context.error = {
                        'type': type(exception).__name__,
                        'message': result.longreprtext or str(exception), # TODO longreprtext can be empty. Search what can be used for it.
                        'traceback': ''.join(traceback.format_tb(exception.tb))
                    }
    except Exception as err:
        logger.error("Couldn't handle error for pytest: {}".format(err))
        pass


def set_attributes_test_item(item, module_item):
    """Set current test case item for thundra trace. 

    Args:
        item (pytest.Item): Current running test case.
    """
    try:
        setattr(item, "scope", "function")  
        setattr(module_item, "scope", "module")
        own_markers = item.own_markers
        check_marked_as_skipped = any("skip" in mark.name for mark in own_markers)
        if check_marked_as_skipped:
            setattr(item, constants.THUNDRA_MARKED_AS_SKIPPED, True)
    except Exception as err:
        logger.error("Couldn't set attributets test item for pytest: {}".format(err))
        pass


def check_test_status_state(item, call):
    """Check current running test case state and return status and exception if any.

    Args:
        item (pytest.Item): Current running test case
        call (pytest.CallInfo): Result/Exception info a function invocation.

    Returns:
        bool: True if test status should be calculated o.w False.
        pytest.ExceptionInfo: Exception info if any else None
    """
    try:
        is_setup_or_teardown = call.when == 'setup' or call.when == 'teardown'
        exception = call.excinfo
        status = True
        if (is_setup_or_teardown and not exception) or hasattr(item, constants.THUNDRA_TEST_RESULTED):
            status = False
        '''
            Pytest not run call when function skipped. So, if function has THUNDRA_MARKED_AS_SKIPPED and
            call.when is call state, then condition for skipif returns false and just evalute result with default.
        '''
        if call.when == "call" and hasattr(item, constants.THUNDRA_MARKED_AS_SKIPPED):
            delattr(item, constants.THUNDRA_MARKED_AS_SKIPPED)
        return status, exception
    except Exception as err:
        logger.error("Couldn't check test status state: {}".format(err))
        pass
    return False, None


def _check_thundra_fixture(request):
    return constants.THUNDRA_FIXTURE_PREFIX in request.fixturename


def _check_request_scope_function(request):
    return request.scope == "function"


def _check_request_scope_fixture(request): #TODO for now, class fixture do not support!!!
    return request.scope == "function" or request.scope == "module"


def fixture_closure(request, setup_or_teardown, start_or_finish):
    """Handle beforeeach, aftereach, beforeall and afterall process for thundra.

    Args:
        request (pytest.FixtureRequest): The request fixture is a special fixture providing information of the requesting test function.
        setup_or_teardown (bool, optional): To decide current state is fixture setup or teardown.
        start_or_finish (bool, optional): To decide span should be started or finished. 
    """
    def handle_fixture_setup():
        if start_or_finish:
            if _check_request_scope_function(request):
                PytestHelper.start_test_span(request.node)
                PytestHelper.start_before_each_span(request)
            else:
                PytestHelper.start_before_all_span(request)
        else:
            if _check_request_scope_function(request):
                PytestHelper.finish_before_each_span(request)
            else:
                PytestHelper.finish_before_all_span(request)  


    def handle_fixture_teardown():
        if start_or_finish:
            if _check_request_scope_function(request):
                PytestHelper.start_after_each_span(request)
            else:
                PytestHelper.start_after_all_span(request)
        else:
            if _check_request_scope_function(request):
                PytestHelper.finish_after_each_span(request)
            else:
                PytestHelper.finish_after_all_span(request)


    if _check_thundra_fixture(request) or not request:
        return
    else:
        if setup_or_teardown:
            handle_fixture_setup()
        else:
            handle_fixture_teardown()



def _wrapper_setup_fixture(wrapped, instance, args, kwargs):
    res = None
    request = None
    try:
        request = args[1]
    except Exception as err:
        logger.error("Couldn't get request in wrapper_setup function: {}".format(err))
    if _check_request_scope_fixture(request):
        fixture_closure(request, setup_or_teardown=True, start_or_finish=True)
        res = wrapped(*args, **kwargs)
        fixture_closure(request, setup_or_teardown=True, start_or_finish=False)
    else:
        res = wrapped(*args, **kwargs)
    if res != None:
        return res



def _wrapper_teardown_fixture(wrapped, instance, args, kwargs):
    request = None
    try:
        request = kwargs["request"]
    except Exception as err:
        logger.error("Couldn't get request in wrapper_teardown function: {}".format(err))
    '''
        Pytest stores fixtures teardown functions in _finalizers list. If there is no 
        teardown function no need to create span.
    '''
    if instance._finalizers and _check_request_scope_fixture(request):
        fixture_closure(request, setup_or_teardown=False, start_or_finish=True)
        wrapped(*args, **kwargs)
        fixture_closure(request, setup_or_teardown=False, start_or_finish=False)
    else:
        wrapped(*args, **kwargs)

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