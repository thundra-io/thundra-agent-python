from threading import Lock

from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.samplers.base_sampler import BaseSampler


class CountAwareSampler(BaseSampler):

    def __init__(self, count_freq=None):
        freq_from_env = ConfigProvider.get(config_names.THUNDRA_SAMPLER_COUNTAWARE_COUNTFREQ, -1)
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
