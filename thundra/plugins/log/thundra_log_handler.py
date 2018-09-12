import logging
from thundra.opentracing.tracer import ThundraTracer

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
            'trace_id': active_span.trace_id,
            'span_id': active_span.span_id,
            'log': formatted_message,
            'logMessage': record.msg,
            'logContextName': record.name,
            'logTimestamp': int(record.created * 1000),
            'logLevel': record.levelname,
            'logLevelCode': record.levelno / 10
        }
        logs.append(log)


logging.ThundraLogHandler = ThundraLogHandler
