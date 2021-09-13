from thundra.context.execution_context import ExecutionContext
from thundra.foresight.test_runner_tags import TestRunnerTags
from thundra.foresight.test_run_context import TestRunContext
import fastcounter


class TestSuiteExecutionContext(TestRunContext, ExecutionContext):

    APPLICATION_DOMAIN_NAME = "TestSuite"

    def __init__(self, **opts):
        super(TestSuiteExecutionContext, self).__init__(**opts)
        self.test_suite_name = opts.test_suite_name or ''
        self.completed = opts.completed or False
        self.closed = opts.closed or False
        self.resource_duration = fastcounter.FastWriteCounter(opts.resource_duration or 0)

    def increase_resources_duration(self, duration=None):
        if not duration:
            self.resources_duration.increment(duration)

    def get_resources_duration(self):
        return self.resources_duration.value


    def get_operation_name(self):
        return self.test_suite_name

    def get_additional_start_tags(self):
        return {
            TestRunnerTags.TEST_SUITE: self.test_suite_name
        }

    def get_additional_finish_tags(self):
        return {
            TestRunnerTags.TEST_SUITE_FAILED_COUNT: self.failedCount,
            TestRunnerTags.TEST_SUITE_TOTAL_COUNT: self.totalCount,
            TestRunnerTags.TEST_SUITE_ABORTED_COUNT: self.abortedCount,
            TestRunnerTags.TEST_SUITE_SKIPPED_COUNT: self.skippedCount,
            TestRunnerTags.TEST_SUITE_SUCCESSFUL_COUNT: self.successfulCount,
            TestRunnerTags.TEST_TIMEOUT: self.timeout
        }