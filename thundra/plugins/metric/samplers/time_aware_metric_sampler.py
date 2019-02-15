import time
from thundra import constants

class TimeAwareMetricSampler:

    def __init__(self, time_freq=None):
        if time_freq is None:
            self.time_freq = constants.DEFAULT_METRIC_SAMPLING_TIME_FREQ
        else:
            self.time_freq = time_freq
        self.latest_time = 0

    def is_sampled(self):
        current_time = 1000 * time.time()
        if current_time > self.latest_time + self.time_freq:
            self.latest_time = current_time
            return True
        return False
