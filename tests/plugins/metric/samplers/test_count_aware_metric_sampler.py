import os
from thundra import constants
from thundra.plugins.metric.samplers import CountAwareMetricSampler

def test_default_count_freq():
    cams = CountAwareMetricSampler()

    assert cams.count_freq == constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ

def test_freq_from_env(monkeypatch):
    count_freq = 37
    monkeypatch.setitem(os.environ, 
        constants.THUNDRA_AGENT_METRIC_COUNT_AWARE_SAMPLER_COUNT_FREQ, '{}'.format(count_freq))

    cams = CountAwareMetricSampler()

    assert cams.count_freq == count_freq

def test_count_freq():
    cams = CountAwareMetricSampler(count_freq=10)
    count_freq = 10
    invocation_count = 100
    expected = invocation_count // count_freq

    res = 0
    for i in range(invocation_count):
        if cams.is_sampled():
            res += 1
    
    assert res == expected

def test_first_invocation_sampled():
    cams = CountAwareMetricSampler(count_freq=10)

    assert cams.is_sampled()

