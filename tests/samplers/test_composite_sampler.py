import mock
import pytest
from catchpoint.samplers import CompositeSampler


@pytest.fixture
def mocked_sampler():
    def sampler(is_sampled=False):
        m = mock.Mock(name='mocked_sampler')
        m.is_sampled.return_value = is_sampled

        return m

    return sampler


def test_with_no_samplers():
    cms = CompositeSampler()

    assert not cms.is_sampled()


def test_and_operator(mocked_sampler):
    s1 = mocked_sampler(is_sampled=False)
    s2 = mocked_sampler(is_sampled=True)
    s3 = mocked_sampler(is_sampled=True)

    cms1 = CompositeSampler(samplers=[s2, s3], operator='and')
    cms2 = CompositeSampler(samplers=[s1, s2, s3], operator='and')

    assert cms1.is_sampled()
    assert not cms2.is_sampled()


def test_or_operator(mocked_sampler):
    s1 = mocked_sampler(is_sampled=True)
    s2 = mocked_sampler(is_sampled=False)
    s3 = mocked_sampler(is_sampled=False)

    cms1 = CompositeSampler(samplers=[s2, s3], operator='or')
    cms2 = CompositeSampler(samplers=[s1, s2, s3], operator='or')

    assert not cms1.is_sampled()
    assert cms2.is_sampled()


def test_with_unknown_operator(mocked_sampler):
    s1 = mocked_sampler(is_sampled=True)
    s2 = mocked_sampler(is_sampled=False)
    s3 = mocked_sampler(is_sampled=False)

    cms1 = CompositeSampler(samplers=[s2, s3], operator='foo')
    cms2 = CompositeSampler(samplers=[s1, s2, s3], operator='foo')

    assert not cms1.is_sampled()
    assert cms2.is_sampled()
