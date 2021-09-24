from thundra.foresight.test_runner_support import TestRunnerSupport

class TestStatus:
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
    SKIPPED = "SKIPPED"
    TOTAL = "TOTAL"

def increase_successful_count():
    test_run_context = TestRunnerSupport.test_run_scope
    test_suite_context = TestRunnerSupport.test_suite_execution_context

    test_run_context.context.increase_successful_count()
    test_suite_context.increase_successful_count()
    _increase_total_count(test_run_context, test_suite_context)


def increase_failed_count():
    test_run_context = TestRunnerSupport.test_run_scope
    test_suite_context = TestRunnerSupport.test_suite_execution_context

    test_run_context.context.increase_failed_count()
    test_suite_context.increase_failed_count()
    _increase_total_count(test_run_context, test_suite_context)


def increase_aborted_count():
    test_run_context = TestRunnerSupport.test_run_scope
    test_suite_context = TestRunnerSupport.test_suite_execution_context

    test_run_context.context.increase_aborted_count()
    test_suite_context.increase_aborted_count()
    _increase_total_count(test_run_context, test_suite_context)


def increase_skipped_count():
    test_run_context = TestRunnerSupport.test_run_scope
    test_suite_context = TestRunnerSupport.test_suite_execution_context

    test_run_context.context.increase_ignored_count()
    test_suite_context.increase_ignored_count() 
    _increase_total_count(test_run_context, test_suite_context)


def _increase_total_count(test_run_context, test_suite_context):
    test_run_context.context.increase_total_count()
    test_suite_context.increase_total_count()


increase_actions = {
    TestStatus.SUCCESSFUL: increase_successful_count,
    TestStatus.FAILED: increase_failed_count,
    TestStatus.ABORTED: increase_aborted_count,
    TestStatus.SKIPPED: increase_skipped_count,
}