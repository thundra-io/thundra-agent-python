import fastcounter
from thundra.foresight.test_run_context import TestRunContext

class TestSuiteContext(TestRunContext):

    def __init__(self, trace_id, transaction_id, span_id):
        super(TestSuiteContext, self).__init__()
        self.trace_id = trace_id
        self.transaction_id = transaction_id
        self.span_id = span_id
        self.resources_duration = fastcounter.FastWriteCounter()

    def increase_resources_duration(self, duration=None):
        if not duration:
            self.resources_duration.increment(duration)

    def get_resources_duration(self):
        return self.resources_duration.value