from thundra import constants
from thundra.plugins.metric.samplers import CountAwareMetricSampler

def test_default_count_freq():
    cams = CountAwareMetricSampler()

    assert cams.count_freq == constants.DEFAULT_METRIC_SAMPLING_COUNT_FREQ

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

