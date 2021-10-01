from thundra.samplers.base_sampler import BaseSampler
import fastcounter

class MaxCountAwareSampler(BaseSampler):

    def __init__(self, max_count):
        self.max_count = max_count
        self.counter = fastcounter.FastWriteCounter()

    def is_sampled(self, args=None):
        self.counter.increment()
        return self.counter.value <= self.max_count