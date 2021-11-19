import pytest, logging, os

from foresight.pytest_integration.utils import (patch, check_test_case_result, 
    update_test_status, set_attributes_test_item, check_test_status_state)
from foresight.pytest_integration.pytest_helper import PytestHelper
from foresight import foresight_executor
import foresight.pytest_integration.constants as pytest_constants
from thundra.context.execution_context_manager import ExecutionContextManager

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Setup thundra for pytest. Adding both ini file and command line argument. 

    Args:
        parser (pytest.Parser): Parser for command line arguments and ini-file values
    """
    try:
        group = parser.getgroup("thundra")

        # config.getoption(markerName) 
        group.addoption(
            "--thundra_disable",
            action="store_true",
            dest="thundra_disable",
            default=False,
            help='THUNDRA_APIKEY and THUNDRA_AGENT_TEST_PROJECT_ID should be set as environment variables. \
                Disable thundra by --thundra_disable argument. ',
        )
        parser.addini("thundra_disable", 'Disable tracing of pytest functions by --thundra_disable argument', type="bool")
    except Exception as e:
        logger.error("Pytest addoption error: {}".format(e))


def check_thundra_from_env():
    check_thundra_api_key = None
    check_thundra_project_id = None
    for key in os.environ.keys():
        lower_key = key.lower()
        if lower_key.startswith("thundra_"):
            if lower_key == "thundra_apikey":
                check_thundra_api_key = True
            elif lower_key == "thundra_agent_test_project_id":
                check_thundra_project_id = True
            if check_thundra_api_key and check_thundra_project_id:
                break
    return check_thundra_api_key, check_thundra_project_id

def check_thundra_test_disabled():
    check_thundra_test_disabled = False
    for key in os.environ.keys():
        lower_key = key.lower()
        if lower_key.startswith("thundra_"):
            if lower_key == "thundra_agent_test_disable":
                check_thundra_test_disabled = False if os.getenv(key).lower() == "false" else True
                break
    return check_thundra_test_disabled

'''
    if thundra is imported in conftest!!!
    example:
        import thundra
        thundra.configure(
        options={
            "config": {
                "thundra.apikey": <test_id>,
                "thundra.agent.test.project.id": <project_id>,
            }
        }
)
'''
def check_thundra_from_conf():
    from thundra.config.config_provider import ConfigProvider
    from thundra.config import config_names
    api_key = ConfigProvider.get(config_names.THUNDRA_APIKEY, None)
    project_id = ConfigProvider.get(config_names.THUNDRA_TEST_PROJECT_ID, None)
    return api_key, project_id


def pytest_load_initial_conftests(early_config, parser, args):
    """Check --collect-only args set by user. If it's set, then there will no any test run. 
    Therefore, no need to start Thundra.

    Args:
        early_config (Config): Pytest Config Object
        parser (Parser): Pytest Parser Object
        args (List[str]): Pytest command line args
    """
    if "--collect-only" in args:
        PytestHelper.set_pytest_collect_only()

def pytest_sessionstart(session):
    """ Check thundra has been activated. If it has been, then start session.

    Args:
        session (pytest.Session): Pytest session class
    """
    try:
        from thundra.config.config_provider import ConfigProvider
        from thundra.config import config_names
        if (session.config.getoption("thundra_disable") or 
            session.config.getini("thundra_disable") or 
            check_thundra_test_disabled() or 
            ConfigProvider.get(config_names.THUNDRA_TEST_DISABLE, False)):
            import thundra 
            already_configured = True if ConfigProvider.configs else False
            thundra._set_thundra_for_test_env(already_configured)
        else:
            api_key_env, project_id_env = check_thundra_from_env()
            api_key_conf, project_id_conf = check_thundra_from_conf()
            check_thundra_project_id = project_id_env or project_id_conf
            check_thundra_api_key = api_key_env or api_key_conf
            if check_thundra_project_id and check_thundra_api_key and not PytestHelper.check_pytest_collect_only():
                PytestHelper.set_pytest_started()
                patch()
                PytestHelper.session_setup(executor=foresight_executor)
            else:
                print("[THUNDRA] Please make sure setting THUNDRA_APIKEY and THUNDRA_AGENT_TEST_PROJECT_ID as environment variables and pytest --collect-only args ain't activated!")
    except Exception as e:
        logger.error("Pytest pytest_sessionstart error: {}".format(e))
        pass

def pytest_sessionfinish(session, exitstatus):
    """ Finish session for thundra

    Args:
        session (pytest.Session): Pytest session class
        exitstatus (int): The status which pytest will return to the system
    """
    try:
        if PytestHelper.check_pytest_started():
            PytestHelper.session_teardown()
    except Exception as e:
        logger.error("Pytest sessionfinish error: {}".format(e))
        pass

@pytest.fixture(scope="function", autouse=True)
def x_thundra_finish_test(request):
    """ If test has a fixture, then finish test case after test case body and 
    all fixture_teardown has been done.

    Args:
        request ([type]): [description]
    """
    try:
        if PytestHelper.check_pytest_started():
            yield
            PytestHelper.finish_test_span(request.node)
        else:
            yield
    except Exception as e:
        logger.error("Pytest x_thundra_finish_test error: {}".format(e))
        pass

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
    try:
        if not PytestHelper.check_pytest_started():
            yield
            return
        module_item = item.getparent(pytest.Module)
        set_attributes_test_item(item, module_item)
        PytestHelper.start_test_suite_span(module_item)
        yield
        if not hasattr(item, pytest_constants.THUNDRA_TEST_FINISH_IN_HELPER):
            PytestHelper.finish_test_span(item)
        else:
            delattr(item, pytest_constants.THUNDRA_TEST_FINISH_IN_HELPER)
        if not nextitem or item.getparent(pytest.Module).nodeid != nextitem.getparent(pytest.Module).nodeid:
            PytestHelper.finish_test_suite_span()
    except Exception as e:
        logger.error("Pytest runtest_protocol error: {}".format(e))
        pass

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
    try:
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
    except Exception as e:
        logger.error("Pytest runtest_makereport error: {}".format(e))
        pass