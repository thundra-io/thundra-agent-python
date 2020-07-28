from thundra import constants
from thundra.samplers import CountAwareSampler
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

def test_default_count_freq():
    cams = CountAwareSampler()

    assert cams.count_freq == constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ


def test_freq_from_env():
    count_freq = 37
    ConfigProvider.set(config_names.THUNDRA_SAMPLER_COUNTAWARE_COUNTFREQ, '{}'.format(count_freq))

    cams = CountAwareSampler()

    assert cams.count_freq == count_freq


def test_count_freq():
    cams = CountAwareSampler(count_freq=10)
    count_freq = 10
    invocation_count = 100
    expected = invocation_count // count_freq

    res = 0
    for i in range(invocation_count):
        if cams.is_sampled():
            res += 1

    assert res == expected


def test_first_invocation_sampled():
    cams = CountAwareSampler(count_freq=10)

    assert cams.is_sampled()
