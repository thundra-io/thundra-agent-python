from thundra.foresight.test_runner_support import TestRunnerSupport
import pytest

from thundra.foresight.pytest_integration.utils import patch, unpatch, handle_error, TestTraceConstants
from thundra.foresight.pytest_integration.pytest_helper import PytestHelper
from thundra.foresight import foresight_executor
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.foresight.test_status import increase_actions, TestStatus

# Register argparse-style options and ini-style config values, called once at the beginning of a test run.
def pytest_addoption(parser):
    group = parser.getgroup("thundra")

    # config.getoption(markerName) 
    group.addoption(
        "--thundra",
        action="store_true",
        dest="thundra",
        default=False,
        help='Default "name" for thundra.',
    )
    # ini style config file
    # https://docs.python.org/3/library/configparser.html
    # config.getini(markerName) 
    parser.addini("thundra", 'Default "name" for thundra.', type="bool")


# Called after the Session object has been created and before performing collection and entering the run test loop.
def pytest_sessionstart(session):
    print("session start")
    patch()
    PytestHelper.session_setup(executor=foresight_executor)
    import thundra

# Called after whole test run finished, right before returning the exit status to the system.
def pytest_sessionfinish(session, exitstatus):
    print("session exit")
    unpatch()
    PytestHelper.session_teardown()

'''
    - Allow plugins and conftest files to perform initial configuration.
    - This hook is called for every plugin and initial conftest file after command line options have been parsed.
    - After that, the hook is called for other conftest files as they are imported.

    If your plugin uses any markers, you should register them so that they appear in pytest’s help text and do not cause spurious warnings
'''
def pytest_configure(config):
    config.addinivalue_line("markers", "thundra_tags(**kwargs): Deneme custom plugin.")


@pytest.fixture(scope="session", autouse=True)
def x_thundra_patch_all(request):
    # import traceback
    # traceback.print_stack()
    arg_name = request.config.getoption("thundra")
    # print("request:",request.session.items)
    # print(arg_name)

@pytest.fixture(scope="function", autouse=True)
def x_thundra_finish_test(request):
    yield
    if not hasattr(request.node, TestTraceConstants.THUNDRA_TEST_ALREADY_FINISHED):
        setattr(request.node, TestTraceConstants.THUNDRA_TEST_ALREADY_FINISHED, True)
        PytestHelper.finish_test_span()

# Perform the runtest protocol for a single test item
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):    
    setattr(item, "scope", "function")  
    setattr(item.parent, "scope", "module")
    own_markers = item.own_markers
    check_marked_as_skipped = any("skip" in mark.name for mark in own_markers)
    if check_marked_as_skipped:
        setattr(item, TestTraceConstants.THUNDRA_MARKED_AS_SKIPPED, True)
    PytestHelper.start_test_suite_span(item.parent)
    yield
    if not hasattr(item, TestTraceConstants.THUNDRA_TEST_ALREADY_FINISHED):
        PytestHelper.finish_test_span()
    if  not nextitem or item.module.__name__ != nextitem.module.__name__:
        PytestHelper.finish_test_suite_span()



# Called to create a _pytest.reports.TestReport for each of the setup, call and teardown runtest phases of a test item
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    if call.when == "setup":
        if not hasattr(item, TestTraceConstants.THUNDRA_TEST_STARTED):
            PytestHelper.start_test_span(item)
    outcome = yield
    is_setup_or_teardown = call.when == 'setup' or call.when == 'teardown'
    exception = call.excinfo #TODO
    if (is_setup_or_teardown and not exception) or hasattr(item, TestTraceConstants.THUNDRA_TEST_RESULTED):
        return
    test_status = TestStatus.SUCCESSFUL
    execution_context = ExecutionContextManager.get()  
    # After Function call report to get test status(success, failed, aborted, skipped , ignored)
    result = outcome.get_result()
    xfail = hasattr(result, "wasxfail") or "xfail" in result.keywords
    has_skip_keyword = any(x in result.keywords for x in ["skip", "skipif"])

    if hasattr(item, TestTraceConstants.THUNDRA_MARKED_AS_SKIPPED):
        delattr(item, TestTraceConstants.THUNDRA_MARKED_AS_SKIPPED)
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
        # Check XPASS TODO
        test_status = TestStatus.SUCCESSFUL
    else: # failed
        test_status = TestStatus.FAILED
        handle_error(exception, result, execution_context)
    increase_action = increase_actions[test_status]
    execution_context.set_status(test_status)
    if increase_action:
        setattr(item, TestTraceConstants.THUNDRA_TEST_RESULTED, True)
        increase_action()

'''
    ignored paths in collection process
    -- ignore
'''
def pytest_ignore_collect(path, config): 
    # print("ignored: ", path)
    pass

'''
    Deselected items should be added into ignored test cases.
    --deselect
'''
def pytest_deselected(items):
    # print("deselected items", items)
    pass

#### Exception and interruption hooks ####
def pytest_internalerror(excrepr, excinfo):
    pass

def pytest_keyboard_interrupt(excinfo):
    pass

# not called when skip raised.
def pytest_exception_interact(node, call, report):
    pass