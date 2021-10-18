import pytest, logging

from foresight.pytest_integration.utils import (patch, check_test_case_result, 
    update_test_status, set_attributes_test_item, check_test_status_state)
from foresight.pytest_integration.pytest_helper import PytestHelper
from foresight import foresight_executor
from thundra.context.execution_context_manager import ExecutionContextManager

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Setup thundra for pytest. Adding both ini file and command line argument. 

    Args:
        parser (pytest.Parser): Parser for command line arguments and ini-file values
    """
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


def pytest_sessionstart(session):
    """ Check thundra has been activated. If it has been, then start session.

    Args:
        session (pytest.Session): Pytest session class
    """
    if session.config.getoption("thundra") or session.config.getini("thundra"):
        PytestHelper.set_pytest_started()
        patch()
        PytestHelper.session_setup(executor=foresight_executor)
    

def pytest_sessionfinish(session, exitstatus):
    """ Finish session for thundra

    Args:
        session (pytest.Session): Pytest session class
        exitstatus (int): The status which pytest will return to the system
    """
    if PytestHelper.check_pytest_started():
        PytestHelper.session_teardown()


@pytest.fixture(scope="function", autouse=True)
def x_thundra_finish_test(request):
    """ If test has a fixture, then finish test case after test case body and 
    all fixture_teardown has been done.

    Args:
        request ([type]): [description]
    """
    if PytestHelper.check_pytest_started():
        yield
        PytestHelper.finish_test_span(request.node)
    else:
        yield


# Perform the runtest protocol for a single test item
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):    
    """Perform the runtest protocol for a single test item. Set attributes for identify 
    item will be used for test suite or test case, and it has any skip marked. 
    Start test suite and after all flow completed and nextitem is None or current item.module not equal to
    nextitem.module finish test suite also.

    Args:
        item (pytest.Item): Test item for which the runtest protocol is performed.
        nextitem (pytest.Item | None):  The scheduled-to-be-next test item (or None if this is the end my friend).
    """
    if not PytestHelper.check_pytest_started():
        yield
        return    
    module_item = item.getparent(pytest.Module)
    set_attributes_test_item(module_item)
    PytestHelper.start_test_suite_span(module_item)
    yield
    PytestHelper.finish_test_span(item)
    if not nextitem or item.getparent(pytest.Module).nodeid != nextitem.getparent(pytest.Module).nodeid:
        PytestHelper.finish_test_suite_span()


# Called to create a _pytest.reports.TestReport for each of the setup, call and teardown runtest phases of a test item
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Called to create a _pytest.reports.TestReport for each of the setup, 
    call and teardown runtest phases of a test item. Check test case span started or not and
    its marked skipped or not. Then, update test status according to test result.

    Args:
        item (pytest.Item): Current running item(test case).
        call (pytest.CallInfo): The CallInfo for the phase.
    """
    outcome = yield
    if not PytestHelper.check_pytest_started():
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
    update_test_status(item, test_status, execution_context)