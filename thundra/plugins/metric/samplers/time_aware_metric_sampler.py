import time
from threading import Lock

from thundra import constants, config

class TimeAwareMetricSampler:

    def __init__(self, time_freq=None):
        freq_from_env = config.time_aware_metric_freq()
        if freq_from_env > 0:
            self.time_freq = freq_from_env
        elif time_freq is not None:
            self.time_freq = time_freq
        else:
            self.time_freq = constants.DEFAULT_METRIC_SAMPLING_TIME_FREQ
        self._latest_time = 0
        self._lock = Lock()

    def is_sampled(self):
        sampled = False
        with self._lock:
            current_time = 1000 * time.time()
            if current_time > self._latest_time + self.time_freq:
                self._latest_time = current_time
                sampled = True
            else:
                sampled = False
        return sampled
