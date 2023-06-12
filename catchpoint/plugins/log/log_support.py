_sampler = None


def get_sampler():
    return _sampler


def set_sampler(sampler):
    global _sampler
    _sampler = sampler
