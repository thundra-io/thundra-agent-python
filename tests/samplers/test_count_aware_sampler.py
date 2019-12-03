import os
from thundra import constants
from thundra.samplers import CountAwareSampler
from thundra.config import utils
property_accessor = utils.get_property_accessor()


def test_default_count_freq():
    cams = CountAwareSampler()

    assert cams.count_freq == constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ


def test_freq_from_env(monkeypatch):
    count_freq = 37
    monkeypatch.setitem(property_accessor.props,
                        constants.THUNDRA_AGENT_METRIC_COUNT_AWARE_SAMPLER_COUNT_FREQ, '{}'.format(count_freq))

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
