from thundra.samplers.base_sampler import BaseSampler

default_operator = 'or'
available_operators = ['and', 'or']


class CompositeSampler(BaseSampler):

    def __init__(self, samplers=None, operator=default_operator):
        if samplers is None:
            samplers = []
        self.samplers = samplers
        if operator in available_operators:
            self.operator = operator
        else:
            self.operator = default_operator

    def is_sampled(self, args=None):
        if len(self.samplers) == 0:
            return False

        if self.operator == 'or':
            sampled = False
            for sampler in self.samplers:
                sampled = sampler.is_sampled(args) or sampled
            return sampled
        elif self.operator == 'and':
            sampled = True
            for sampler in self.samplers:
                sampled = sampler.is_sampled(args) and sampled
            return sampled
