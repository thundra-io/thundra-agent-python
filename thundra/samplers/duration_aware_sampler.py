from thundra.samplers.base_sampler import BaseSampler


class DurationAwareSampler(BaseSampler):

    def __init__(self, duration, longer_than=False):
        self.duration = duration
        self.longer_than = longer_than

    def is_sampled(self, span=None):
        if not span:
            return False

        if self.longer_than:
            return span.get_duration() > self.duration

        return span.get_duration() <= self.duration
