from thundra.samplers.base_sampler import BaseSampler


class ErrorAwareSampler(BaseSampler):

    def __init__(self):
        pass

    def is_sampled(self, span=None):
        if not span:
            return False

        return span.get_tag("error")
