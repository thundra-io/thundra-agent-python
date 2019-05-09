from thundra.samplers import (
    TimeAwareSampler, CountAwareSampler,
    CompositeSampler
)

_sampler = CompositeSampler(
    samplers=[
        TimeAwareSampler(),
        CountAwareSampler()
    ],
    operator='or'
)


def get_sampler():
    return _sampler


def set_sampler(sampler):
    global _sampler
    _sampler = sampler
