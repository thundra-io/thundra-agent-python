from thundra.foresight.pytest_integration.pytest_helper import PytestHelper
from thundra.foresight.test_status import increase_actions, TestStatus
import thundra.foresight.pytest_integration.constants as constants
import wrapt, logging, traceback

logger = logging.getLogger(__name__)


def check_test_case_result(item, execution_context, result, exception):
    test_status = TestStatus.SKIPPED
    try:
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
    except Exception as err:
        logger.error("Couldn't set test status properly {} for pytest".format(item), err)
    return test_status


def update_test_status(item, test_status, execution_context):
    try:
        increase_action = increase_actions[test_status]
        execution_context.set_status(test_status)
        if increase_action:
            setattr(item, constants.THUNDRA_TEST_RESULTED, True)
            increase_action()
    except Exception as err:
        logger.error("Couldn't update test status {} for pytest".format(item), err)


def handle_error(exception, result, execution_context):
    try:
        execution_context.error = {
                        'type': type(exception).__name__,
                        'message': result.longreprtext,
                        'traceback': ''.join(traceback.format_tb(exception.tb))
                    }
    except Exception as err:
        logger.error("Couldn't handle error for pytest", err)


def set_attributes_test_item(item):
    try:
        setattr(item, "scope", "function")  
        setattr(item.parent, "scope", "module")
        own_markers = item.own_markers
        check_marked_as_skipped = any("skip" in mark.name for mark in own_markers)
        if check_marked_as_skipped:
            setattr(item, constants.THUNDRA_MARKED_AS_SKIPPED, True)
    except Exception as err:
        logger.error("Couldn't set attributets test item {} for pytest".format(item), err)


def check_test_status_state(item, call):
    try:
        is_setup_or_teardown = call.when == 'setup' or call.when == 'teardown'
        exception = call.excinfo
        status = True
        if (is_setup_or_teardown and not exception) or hasattr(item, constants.THUNDRA_TEST_RESULTED):
            status = False
        return status, exception
    except Exception as err:
        logger.error("Couldn't check test status state", err)
        return False, None


def _check_thundra_fixture(request):
    return constants.THUNDRA_FIXTURE_PREFIX in request.fixturename


def _check_request_scope_function(request):
    return request.scope == "function"


def fixture_closure(request, setup_or_teardown=None, start_or_finish=None):
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
        logger.error("Couldn't get request in wrapper_setup function", err)
    fixture_closure(request, setup_or_teardown=True, start_or_finish=True)
    res = wrapped(*args, **kwargs)
    fixture_closure(request, setup_or_teardown=True, start_or_finish=False)
    if res:
        return res



def _wrapper_teardown_fixture(wrapped, instance, args, kwargs):
    request = None
    try:
        request = kwargs["request"]
    except Exception as err:
        logger.error("Couldn't get request in wrapper_teardown function", err)
    fixture_closure(request, setup_or_teardown=False, start_or_finish=True)
    wrapped(*args, **kwargs)
    fixture_closure(request, setup_or_teardown=False, start_or_finish=False)


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