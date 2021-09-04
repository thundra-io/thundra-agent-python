import fastcounter

class TestRunContext:

    def __init__(self):
        self.total_count = fastcounter.FastWriteCounter()
        self.successful_count = fastcounter.FastWriteCounter()
        self.failed_count = fastcounter.FastWriteCounter()
        self.ignored_count = fastcounter.FastWriteCounter()
        self.aborted_count = fastcounter.FastWriteCounter()

    def increase_total_count(self):
        self.total_count.increment()

    def increase_successful_count(self):
        self.successful_count.increment()

    def increase_failcleared_count(self):
        self.failed_count.increment()

    def increase_ignored_count(self):
        self.ignored_count.increment()

    def increase_aborted_count(self):
        self.aborted_count.increment()
    
    def get_total_count(self):
        return self.total_count.value

    def get_successful_count(self):
        return self.successful_count.value

    def get_failed_count(self):
        return self.failed_count.value

    def get_ignored_count(self):
        return self.ignored_count.value

    def get_aborted_count(self):
        return self.aborted_count.value