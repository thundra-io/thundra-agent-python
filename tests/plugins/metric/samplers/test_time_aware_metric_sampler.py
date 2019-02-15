import mock
from thundra import constants
from thundra.plugins.metric.samplers import TimeAwareMetricSampler

def test_default_time_freq():
    tams = TimeAwareMetricSampler()

    assert tams.time_freq == constants.DEFAULT_METRIC_SAMPLING_TIME_FREQ

@mock.patch('time.time')
def test_time_freq(mocked_time):
    tams = TimeAwareMetricSampler()

    cases = [
        {
            'lt': 0,    # Latest time
            'ct': 30,   # Current time
            'f': 37,    # Frequency
            'e': False, # Expexted
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