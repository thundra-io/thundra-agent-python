
default_operator = 'or'
avaiable_operators = ['and', 'or']

class CompositeMetricSampler:
    
    def __init__(self, samplers=[], operator=default_operator):
        self.samplers = samplers
        if operator in avaiable_operators:
            self.operator = operator
        else:
            self.operator = default_operator
    
    def is_sampled(self):
        if len(self.samplers) == 0:
            return False
        
        if self.operator == 'or':
            sampled = False
            for sampler in self.samplers:
                sampled = sampler.is_sampled() or sampled
            return sampled
        elif self.operator == 'and':
            sampled = True
            for sampler in self.samplers:
                sampled = sampler.is_sampled() and sampled
            return sampled
