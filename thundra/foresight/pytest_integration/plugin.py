import pytest

from thundra.foresight.pytest_integration.utils import (patch, check_test_case_result, 
    handle_test_status, set_attributes_test_item, check_test_status_state)
from thundra.foresight.pytest_integration.pytest_helper import PytestHelper
from thundra.foresight import foresight_executor
from thundra.context.execution_context_manager import ExecutionContextManager

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
    parser.addini("thundra", 'Enable tracing of pytest functions by --thundra argument', type="bool")


# Called after the Session object has been created and before performing collection and entering the run test loop.
def pytest_sessionstart(session):
    if session.config.getoption("thundra") or session.config.getini("thundra"):
        PytestHelper.PYTEST_STARTED = True
        patch()
        import thundra
        PytestHelper.session_setup(executor=foresight_executor)
    

# Called after whole test run finished, right before returning the exit status to the system.
def pytest_sessionfinish(session, exitstatus):
    if PytestHelper.PYTEST_STARTED:
        PytestHelper.session_teardown()


@pytest.fixture(scope="function", autouse=True)
def x_thundra_finish_test(request):
    if PytestHelper.PYTEST_STARTED:
        yield
        PytestHelper.finish_test_span(request.node)
    else:
        yield


# Perform the runtest protocol for a single test item
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):    
    if not PytestHelper.PYTEST_STARTED:
        yield
        return
    set_attributes_test_item(item)
    PytestHelper.start_test_suite_span(item.parent)
    yield
    PytestHelper.finish_test_span(item)
    if  not nextitem or item.module.__name__ != nextitem.module.__name__:
        PytestHelper.finish_test_suite_span()


# Called to create a _pytest.reports.TestReport for each of the setup, call and teardown runtest phases of a test item
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if not PytestHelper.PYTEST_STARTED:
        return
    if call.when == "setup":
            PytestHelper.start_test_span(item)
    status, exception = check_test_status_state(item, call)
    if not status:
        return
    result = outcome.get_result()
    execution_context = ExecutionContextManager.get()  
    # After Function call report to get test status(success, failed, aborted, skipped , ignored)
    test_status = check_test_case_result(item, execution_context, result, exception)
    handle_test_status(item, test_status, execution_context)


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