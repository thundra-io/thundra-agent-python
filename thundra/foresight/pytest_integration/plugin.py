import pytest

from thundra.foresight.pytest_integration.utils import patch, unpatch, check_mark_skip_test
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


'''
    Create useful data structures fro test_suites and test_runs

    - Synchronized Map<nodeid: String, ThundraScope> testDescriptionScopeMap
    - Synchronized Map<item.location[FILENAME]: String, TestSuiteContext> TestSuiteContexts. It will be used into pytest_runtest_makereport
    foreach item in request.session.items:
        item.location => A tuple of (filename(Full test path), lineno, testname)
        - location enums like FILENAME(0), LINENO(1), OPERATION_NAME(2)
        - test_suite_name => index = item.location[FILENAME].rfind(os.sep) and return item.location[FILENAME][index+1:] 

        item.nodeid => Test runner scope store id(TestRunnerScopeStore.getDescriptionId)
        - testDescriptionScopeMap[item.nodeid] = ThundraScope
        - if not "test_suite_name" in TestSuiteContexts.keys():
            - TestSuiteContexts[test_suite_name] = TestSuiteContext
'''
@pytest.fixture(scope="session", autouse=True)
def x_thundra_patch_all(request):
    # import traceback
    # traceback.print_stack()
    arg_name = request.config.getoption("thundra")
    # print("request:",request.session.items)
    # print(arg_name)


@pytest.fixture(scope="function", autouse=True)
def x_thundra_function_fix(request):
    PytestHelper.start_test_span(request)
    yield
    PytestHelper.finish_test_span()


@pytest.fixture(scope="module", autouse=True)
def x_thundra_module_fix(request):
    PytestHelper.start_test_suite_span(request)
    yield
    PytestHelper.finish_test_suite_span()
    

'''
    test_suite_name = index = item.location[FILENAME].rfind(os.sep) and return item.location[FILENAME][index+1:] 
    - if not TestSuiteContexts[test_suite_name].start:
        TestSuiteContexts[test_suite_name].start = time.now()
    
   beforeClass, afterClass, beforeAll, afterAll 
'''
# Perform the runtest protocol for a single test item
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    yield



# Called to create a _pytest.reports.TestReport for each of the setup, call and teardown runtest phases of a test item
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    # TODO Check skipped tests.
    is_setup_or_teardown = call.when == 'setup' or call.when == 'teardown'
    exception = call.excinfo #TODO
    if is_setup_or_teardown and not exception and not hasattr(item, "marked_as_skipped"):
        return
    marked_as_skipped = check_mark_skip_test(item, call)
    if marked_as_skipped:
        return
    test_status = TestStatus.SUCCESSFUL
    execution_context = ExecutionContextManager.get()  
    # After Function call report to get test status(success, failed, aborted, skipped , ignored)
    result = outcome.get_result()
    xfail = hasattr(result, "wasxfail") or "xfail" in result.keywords
    has_skip_keyword = any(x in result.keywords for x in ["skip", "skipif"])
    if result.skipped:
        if xfail and not has_skip_keyword:
            test_status = TestStatus.SUCCESSFUL
        else:
            test_status = TestStatus.SKIPPED
    elif result.passed:
        # Check XPASS TODO
        test_status = TestStatus.SUCCESSFUL
    else: # failed
        test_status = TestStatus.FAILED
        import traceback
        execution_context.error = {
                        'type': type(exception).__name__,
                        'message': result.longreprtext,
                        'traceback': ''.join(traceback.format_tb(exception.tb))
                    }
    increase_action = increase_actions[test_status]
    execution_context.set_status(test_status)
    if increase_action:
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