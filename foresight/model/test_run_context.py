import fastcounter

class TestRunContext:

    def __init__(self, total_count=0, successful_count = 0, failed_count=0, ignored_count=0, 
        aborted_count=0, **ignored):
        self.total_count = fastcounter.FastWriteCounter(total_count)
        self.successful_count = fastcounter.FastWriteCounter(successful_count)
        self.failed_count = fastcounter.FastWriteCounter(failed_count)
        self.ignored_count = fastcounter.FastWriteCounter(ignored_count)
        self.aborted_count = fastcounter.FastWriteCounter(aborted_count)

    def increase_total_count(self, count=1):
        self.total_count.increment(count)

    def increase_successful_count(self):
        self.successful_count.increment()

    def increase_failed_count(self):
        self.failed_count.increment()

    def increase_ignored_count(self, count=1):
        self.ignored_count.increment(count)

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