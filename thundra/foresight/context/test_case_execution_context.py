from thundra.context.execution_context import ExecutionContext
from thundra.foresight.test_runner_tags import TestRunnerTags

class TestCaseExecutionContext(ExecutionContext):

    def __init__(self, **opts):
        super(TestCaseExecutionContext, self).__init__(**opts)
        self.id = opts.id or '' # id = nodeid
        self.name = opts.name or ''
        self.method = opts.method or ''
        self.test_class = opts.test_class or ''
        self.test_suite_name = opts.test_suite_name or ''

    def set_status(self, status):
        self.status = status

    def get_operation_name(self):
        return self.id

    def get_additional_start_tags(self):
        return {
            TestRunnerTags.TEST_NAME: self.name,
            TestRunnerTags.TEST_SUITE: self.test_suite_name,
            TestRunnerTags.TEST_METHOD: self.method,
            TestRunnerTags.TEST_CLASS: self.test_class
        }

    def get_additional_finish_tags(self):
        return {
            TestRunnerTags.TEST_STATUS: self.status
        }