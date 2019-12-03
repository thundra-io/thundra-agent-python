from threading import Lock
from thundra import constants
from thundra.samplers.base_sampler import BaseSampler
from thundra.config import utils as config_utils

class CountAwareSampler(BaseSampler):

    def __init__(self, count_freq=None):
        freq_from_env = config_utils.get_int_property(constants.THUNDRA_AGENT_METRIC_COUNT_AWARE_SAMPLER_COUNT_FREQ)
        if freq_from_env > 0:
            self.count_freq = freq_from_env
        elif count_freq is not None:
            self.count_freq = count_freq
        else:
            self.count_freq = constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ

        self._counter = -1
        self._lock = Lock()

    def is_sampled(self, args=None):
        return self._increment_and_get_counter() % self.count_freq == 0

    def _increment_and_get_counter(self):
        with self._lock:
            self._counter += 1

        return self._counter
