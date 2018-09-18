import logging
from thundra.opentracing.tracer import ThundraTracer
import uuid

logs = []


class ThundraLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        ThundraLogHandler.logs = []
        self.tracer = ThundraTracer.getInstance()
        self.scope = None

    def emit(self, record):
        formatted_message = self.format(record)
        active_span = self.tracer.get_active_span()
        log = {
            'id': str(uuid.uuid4()),
            'applicationDomainName': active_span.domain_name or '' if active_span is not None else '',
            'applicationClassName': active_span.class_name or '' if active_span is not None else '',
            'trace_id': active_span.trace_id if active_span is not None else '',
            'span_id': active_span.span_id if active_span is not None else '',
            'log': formatted_message,
            'logMessage': record.msg,
            'logContextName': record.name,
            'logTimestamp': int(record.created * 1000),
            'logLevel': record.levelname,
            'logLevelCode': int(record.levelno / 10)
        }
        logs.append(log)


logging.ThundraLogHandler = ThundraLogHandler
