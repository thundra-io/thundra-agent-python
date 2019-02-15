from threading import Lock
from thundra import constants

class CountAwareMetricSampler:

    def __init__(self, count_freq=None):
        if count_freq is None:
            self.count_freq = constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ
        else:
            self.count_freq = count_freq
        self._counter = 0
        self._lock = Lock()

    def is_sampled(self):
        return self._increment_and_get_counter() % self.count_freq == 0

    def _increment_and_get_counter(self):
        with self._lock:
            self._counter += 1
        
        return self._counter
