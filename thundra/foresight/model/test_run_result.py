class TestRunResult:

    def __init__(self, total_count, successful_count, failed_count,
     ignored_count, aborted_count):
        self.total_count = total_count
        self.successful_count = successful_count
        self.failed_count = failed_count
        self.ignored_count = ignored_count
        self.aborted_count = aborted_count

    def to_json(self):
        return {
            "totalCount" : self.total_count,
            "successfulCount" : self.successful_count,
            "failedCount" : self.failed_count,
            "ignoredCount" : self.ignored_count,
            "abortedCount" : self.aborted_count,
        }