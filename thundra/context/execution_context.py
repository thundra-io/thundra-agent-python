from thundra.opentracing.recorder import ThundraRecorder


class ExecutionContext:
    """
    Represents the scope of execution (request, invocation, etc ...)
    and holds scope specific data.
    """

    def __init__(self, **opts):
        self.start_timestamp = opts.get('start_timestamp', 0)
        self.finish_timestamp = opts.get('finish_timestamp', 0)
        self.recorder = opts.get('recorder', ThundraRecorder())
        self.reports = opts.get('reports', [])
        self.transaction_id = opts.get('transaction_id', '')
        self.span_id = opts.get('span_id', '')
        self.trace_id = opts.get('trace_id')
        self.root_span = opts.get('root_span')
        self.scope = opts.get('scope')
        self.invocation_data = opts.get('invocation_data')
        self.user_tags = opts.get('user_tags', {})
        self.tags = opts.get('tags', {})
        self.error = opts.get('error')
        self.user_error = opts.get('user_error')
        self.platform_data = opts.get('platform_data', {})
        self.response = opts.get('response', {})
        self.incoming_trace_links = opts.get('incoming_trace_links', [])
        self.outgoing_trace_links = opts.get('outgoing_trace_links', [])
        self.timeout = opts.get('timeout', False)
        self.logs = opts.get('logs', [])
        self.metrics = opts.get('metrics', {})
        self.capture_log = False

    def report(self, data):
        """
        Adds data to be reported
        @param data data to be reported
        """
        if isinstance(data, list):
            for report in data:
                self.reports.append(report)
        else:
            self.reports.append(data)
