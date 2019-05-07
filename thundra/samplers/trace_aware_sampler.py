from thundra.samplers.base_sampler import BaseSampler


class TraceAwareSampler(BaseSampler):

    def __init__(self, trace_id=None, transaction_id=None, sample_non_traced=False):
        self.trace_id = trace_id
        self.transaction_id = transaction_id
        self.sample_non_traced = sample_non_traced

    def is_sampled(self, data=None):
        if not data:
            return True
        if self.trace_id is None:
            if self.transaction_id is None:
                return True
            else:
                transaction_id = data.get('transaction_id')
                if transaction_id is None:
                    return self.sample_non_traced
                return self.transaction_id == transaction_id
        else:
            trace_id = data.get('trace_id')
            if trace_id is None:
                return self.sample_non_traced
            if trace_id == self.trace_id:
                if self.transaction_id is None:
                    return True
                else:
                    transaction_id = data.get('transaction_id')
                    if transaction_id is None:
                        return self.sample_non_traced
                    return self.transaction_id == transaction_id
            else:
                return False
