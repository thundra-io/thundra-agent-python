from thundra.plugins.config.log_config import LogConfig
from thundra.plugins.config.metric_config import MetricConfig
from thundra.plugins.config.trace_config import TraceConfig


class ThundraConfig:
    def __init__(self, opts=None):
        if opts is None:
            opts = {}

        self.api_key = opts.get('apiKey')
        self.disable_thundra = opts.get('disableThundra')
        self.trace_config = TraceConfig(opts.get('traceConfig'))
        self.metric_config = MetricConfig(opts.get('metricConfig'))
        self.log_config = LogConfig(opts.get('logConfig'))
