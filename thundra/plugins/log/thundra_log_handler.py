import uuid
import logging
from thundra.opentracing.tracer import ThundraTracer
from thundra.context.execution_context_manager import ExecutionContextManager


class ThundraLogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self.tracer = ThundraTracer.get_instance()

    def emit(self, record):
        formatted_message = self.format(record)
        execution_context = ExecutionContextManager.get()
        log = {
            'id': str(uuid.uuid4()),
            'spanId': execution_context.span_id if execution_context is not None else '',
            'logMessage': formatted_message,
            'logContextName': record.name,
            'logTimestamp': int(record.created * 1000),
            'logLevel': record.levelname,
            'logLevelCode': int(record.levelno / 10)
        }
        execution_context.logs.append(log)


logging.ThundraLogHandler = ThundraLogHandler
