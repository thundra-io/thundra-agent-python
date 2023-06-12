from __future__ import division
import mock
from catchpoint import constants
from catchpoint.samplers import TimeAwareSampler
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names


def test_default_time_freq():
    tams = TimeAwareSampler()

    assert tams.time_freq == constants.DEFAULT_METRIC_SAMPLING_TIME_FREQ


def test_freq_from_env():
    time_freq = 37
    ConfigProvider.set(config_names.CATCHPOINT_SAMPLER_TIMEAWARE_TIMEFREQ, '{}'.format(time_freq))
    tams = TimeAwareSampler()

    assert tams.time_freq == time_freq


@mock.patch('time.time')
def test_time_freq(mocked_time):
    tams = TimeAwareSampler()

    cases = [
        {
            'lt': 0,  # Latest time
            'ct': 30,  # Current time
            'f': 37,  # Frequency
            'e': False,  # Expexted
        },
        {
            'lt': 0,
            'ct': 38,
            'f': 37,
            'e': True,
        },
    ]

    for case in cases:
        tams.time_freq = case['f']
        tams._latest_time = case['lt']
        mocked_time.return_value = case['ct'] / 1000

        assert tams.is_sampled() == case['e']
