import uuid
import logging
from thundra.opentracing.tracer import ThundraTracer

logs = []


class ThundraLogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        ThundraLogHandler.logs = []
        self.tracer = ThundraTracer.get_instance()

    def emit(self, record):
        formatted_message = self.format(record)
        active_span = self.tracer.get_active_span()
        log = {
            'id': str(uuid.uuid4()),
            'spanId': active_span.context.span_id if active_span is not None else '',
            'log': formatted_message,
            'logMessage': str(record.msg),
            'logContextName': record.name,
            'logTimestamp': int(record.created * 1000),
            'logLevel': record.levelname,
            'logLevelCode': int(record.levelno / 10)
        }
        logs.append(log)


logging.ThundraLogHandler = ThundraLogHandler
