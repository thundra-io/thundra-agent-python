

class TraceAwareMetricSampler:

    def __init__(self, trace_id=None, transaction_id=None, sample_non_traced=False):
        self.trace_id = trace_id
        self.transaction_id = transaction_id
        self.sample_non_traced = sample_non_traced

    def is_sampled(metric_data):
        if self.trace_id is None:
            if self.transaction_id is None:
                return True
            else:
                metric_transaction_id = metric_data.get('transaction_id')
                if metric_transaction_id is None:
                    return self.sample_non_traced
                return self.transaction_id == metric_transaction_id
        else:
            metric_trace_id = metric_data.get('trace_id')
            if metric_trace_id is None:
                return self.sample_non_traced
            if metric_trace_id == self.trace_id:
                if self.transaction_id is None:
                    return True
                else:
                    metric_transaction_id = metric_data.get('transaction_id')
                    if metric_transaction_id is None:
                        return self.sample_non_traced
                    return self.transaction_id == metric_transaction_id
            else:
                return False
