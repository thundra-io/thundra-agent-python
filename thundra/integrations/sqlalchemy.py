import traceback
import time
import logging
from thundra import config, constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.rdb_base import RdbBaseIntegration
from thundra.opentracing.tracer import ThundraTracer

from sqlalchemy.event import listen

logger = logging.getLogger(__name__)


class SqlAlchemyIntegration(RdbBaseIntegration):
    CLASS_TYPE = 'sqlalchemy'

    def __init__(self):
        self.scope = None

    def get_operation_name(self, conn):
        operation_name = ""
        try:
            _url = conn.engine.url
            if _url.host:
                operation_name = _url.host

            if _url.database:
                operation_name = _url.database
        except:
            pass

        return operation_name

    def before_call(self, conn, statement):
        self.scope.span.class_name = constants.ClassNames['SQLALCHEMY']
        self.scope.span.domain_name = constants.DomainNames['DB']

        try:
            operation = statement.split()[0].strip("\"").lower()
        except:
            operation = ""

        tags = {
            constants.SpanTags['OPERATION_TYPE']: SqlAlchemyIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: conn.engine.url.database or "",
            constants.SpanTags['DB_HOST']: conn.engine.url.host or "",
            constants.SpanTags['DB_TYPE']: conn.engine.name or "",
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: "AWS-Lambda",
            constants.SpanTags['TRIGGER_CLASS_NAME']: "API",
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME
        }

        if not config.rdb_statement_masked():
            tags[constants.DBTags['DB_STATEMENT']] = statement

        self.scope.span.tags = tags

    def after_call(self, conn, statement):
        pass

    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        tracer = ThundraTracer.get_instance()

        self.scope = tracer.start_active_span(operation_name=self.get_operation_name(conn), finish_on_close=False)

        # Inject before span tags
        try:
            self.before_call(conn, statement)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            self.scope.span.set_tag('instrumentation_error', e)

        try:
            # Inform span that initialization completed
            self.scope.span.on_started()
        except Exception as e:
            logger.error(e)

    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):

        # Inject after span tags 
        try:
            self.after_call(conn, statement)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            self.scope.span.set_tag('instrumentation_error', e)

        try:
            self.scope.span.finish()
        except Exception as e:
            logger.error(e)

        self.scope.close()

    def _handle_error(self, exception_context):
        self.scope.span.set_tag('error.stack', traceback.format_exc())
        self.scope.span.set_error_to_tag(exception_context.original_exception)

    def trace_engine(self, engine):
        listen(engine, 'before_cursor_execute', self._before_cursor_execute)
        listen(engine, 'after_cursor_execute', self._after_cursor_execute)
        listen(engine, 'handle_error', self._handle_error)
