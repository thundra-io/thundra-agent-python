import traceback
import time
import logging
from thundra import config, constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.rdb_base import RdbBaseIntegration
from thundra.opentracing.tracer import ThundraTracer

try:
    from sqlalchemy.event import listen
    from sqlalchemy.engine.interfaces import ExecutionContext
except:
    pass

logger = logging.getLogger(__name__)


class SqlAlchemyIntegration(RdbBaseIntegration):
    CLASS_TYPE = 'sqlalchemy'

    def __init__(self, engine):
        listen(engine, 'before_cursor_execute', self._before_cursor_execute)
        listen(engine, 'after_cursor_execute', self._after_cursor_execute)
        try:
            listen(engine, 'handle_error', self._handle_error)
        except:
            listen(engine, 'dbapi_error', self._db_api_error)

    def get_operation_name(self, conn):
        return self.get_db_config(conn).get('operation_name', '')

    def get_db_config(self, conn):
        params = {}
        try:
            db_name = conn.engine.name
            if 'postgres' in db_name or 'psycopg2' in db_name:
                params['db_type'] = 'postgresql'
            elif 'sqlite' in db_name:
                params['db_type'] = 'sqlite'
            elif 'mysql' in db_name:
                params['db_type'] = 'mysql'
            else:
                params['db_type'] = db_name

            _url = conn.engine.url
            if _url.host:
                params['host'] = _url.host
                params['operation_name'] = _url.host

            if _url.database:
                params['database'] = _url.database
                params['operation_name'] = _url.database
        except:
            pass

        return params

    def before_call(self, scope, conn, statement):
        db_config = self.get_db_config(conn)

        scope.span.class_name = constants.ClassNames.get(db_config.get('db_type', '').upper())
        scope.span.domain_name = constants.DomainNames['DB']

        try:
            operation = statement.split()[0].strip("\"").lower()
        except:
            operation = ""


        tags = {
            constants.SpanTags['OPERATION_TYPE']: SqlAlchemyIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: db_config.get('database', ''),
            constants.SpanTags['DB_HOST']: db_config.get('host', ''),
            constants.SpanTags['DB_TYPE']: db_config.get('db_type', ''),
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: 'AWS-Lambda',
            constants.SpanTags['TRIGGER_CLASS_NAME']: 'API',
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME
        }

        if not config.rdb_statement_masked():
            tags[constants.DBTags['DB_STATEMENT']] = statement

        scope.span.tags = tags

    def after_call(self, scope, conn, statement):
        pass

    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        if not context:
            return
        tracer = ThundraTracer.get_instance()

        if not tracer.get_active_span():
            return
        scope = tracer.start_active_span(operation_name=self.get_operation_name(conn), finish_on_close=False)

        context.scope = scope

        # Inject before span tags
        try:
            self.before_call(scope, conn, statement)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            scope.span.set_tag('instrumentation_error', e)

        try:
            # Inform span that initialization completed
            scope.span.on_started()
        except Exception as e:
            logger.error(e)

    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        try:
            scope = context.scope
        except:
            return
        # Inject after span tags 
        try:
            self.after_call(scope, conn, statement)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            scope.span.set_tag('instrumentation_error', e)

        try:
            scope.span.finish()
        except Exception as e:
            logger.error(e)

        scope.close()

    def _set_exception(self, conn, statement, context, exception):
        try:
            scope = context.scope
        except:
            return

        try:
            scope.span.set_error_to_tag(exception)
        finally:
            scope.span.finish()
            scope.close()

    def _db_api_error(self, conn, cursor, statement, parameters, context, exception):
        self._set_exception(conn, statement, context, exception)

    def _handle_error(self, exception_context):
        self._set_exception(exception_context.connection, exception_context.statement,
                            exception_context.execution_context, exception_context.original_exception)
