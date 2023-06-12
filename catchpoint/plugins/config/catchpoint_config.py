from catchpoint.plugins.config.log_config import LogConfig
from catchpoint.plugins.config.metric_config import MetricConfig
from catchpoint.plugins.config.trace_config import TraceConfig


class CatchpointConfig:
    def __init__(self, opts=None):
        if opts is None:
            opts = {}

        self.api_key = opts.get('apiKey')
        self.disable_catchpoint = opts.get('disableCatchpoint')
        self.trace_config = TraceConfig(opts.get('traceConfig'))
        self.metric_config = MetricConfig(opts.get('metricConfig'))
        self.log_config = LogConfig(opts.get('logConfig'))
