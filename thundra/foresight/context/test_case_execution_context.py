from thundra.context.execution_context import ExecutionContext
from thundra.foresight.test_runner_tags import TestRunnerTags

class TestCaseExecutionContext(ExecutionContext):

    def __init__(self, **opts):
        super(TestCaseExecutionContext, self).__init__(**opts)
        self.node_id = opts.get("node_id", "")
        self.name = opts.get("name", "")
        self.method = opts.get("method", "")
        self.test_class = opts.get("test_class", '')
        self.test_suite_name = opts.get("test_suite_name", "")
        self.parent_transaction_id = opts.get("parent_transaction_id", "")
        self.status = opts.get("status", "")

    def set_status(self, status):
        self.status = status

    def get_operation_name(self):
        return self.node_id

    def get_additional_start_tags(self):
        return {
            TestRunnerTags.TEST_NAME: self.name,
            TestRunnerTags.TEST_SUITE: self.test_suite_name,
            TestRunnerTags.TEST_METHOD: self.method,
            TestRunnerTags.TEST_CLASS: self.test_class,
            TestRunnerTags.TEST_SUITE_TRANSACTION_ID: self.parent_transaction_id
        }

    def get_additional_finish_tags(self):
        return {
            TestRunnerTags.TEST_STATUS: self.status
        }