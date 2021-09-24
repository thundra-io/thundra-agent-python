from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.foresight.test_runner_support import TestRunnerSupport
import wrapt
from thundra.foresight.pytest_integration.pytest_helper import PytestHelper, HandleSpan
from thundra.foresight.test_status import increase_actions, TestStatus
"""
    Refactor this file. It's been written rapidly.
"""

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

class TestSkipRequest:
    def __init__(self, item):
        self.node = self.Node(item.nodeid, item.location)
        self.scope = "function"

    class Node:
        def __init__(self, nodeid, location):
            self.nodeid = nodeid
            self.location = location

# Tests that are marked by skip or skipif
def check_mark_skip_test(item, call): #TODO
    request = TestSkipRequest(item)
    marked_skipped = False
    if call.when == "teardown":
        check_skip_mark = getattr(item, "marked_as_skipped", None)
        if check_skip_mark:
            context = ExecutionContextManager.get()
            test_status = TestStatus.SKIPPED
            context.set_status(TestStatus.SKIPPED)
            increase_actions[test_status]()
            marked_skipped = True
            PytestHelper.finish_test_span()
    else:
        own_markers = item.own_markers
        check_marked_as_skipped = any("skip" in mark.name for mark in own_markers)
        if check_marked_as_skipped:
            setattr(item, "marked_as_skipped", check_marked_as_skipped)
            marked_skipped = True
            # check test suite started or not 
            if not TestRunnerSupport.test_suite_execution_context:
                node_id = request.node.nodeid
                request.node.nodeid = request.node.location[0]
                request.scope = "module"
                PytestHelper.start_test_suite_span(request)
                request.node.nodeid = node_id
                request.scope = "function"
            # start test case for skipped test and set skipped attr in item
            if TestRunnerSupport.test_case_execution_context:
                return
            else:
                PytestHelper.start_test_span(request)

    return marked_skipped

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
