import psycopg2
from psycopg2 import Error as PostgreError

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer


def test_postgre_integration():
    query = "select 1 + 1 AS solution"

    connection = psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        for table in cursor.fetchall():
            print(table)

    finally:
        tracer = CatchpointTracer.get_instance()
        postgre_span = tracer.get_spans()[1]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'

        connection.close()


def test_postgre_integration_mask_statement():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK, 'true')
    query = "select 1 + 1 AS solution"

    connection = psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        for table in cursor.fetchall():
            print(table)

    finally:
        tracer = CatchpointTracer.get_instance()
        postgre_span = tracer.get_spans()[1]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) is None
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'

        connection.close()


def test_postgre_integration_with_empty_query():
    connection = psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.execute('')
        for table in cursor.fetchall():
            print(table)
    except PostgreError:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        postgre_span = tracer.get_spans()[1]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) is ''
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == ''
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == ''

        connection.close()


def test_postgre_integration_callproc():
    connection = psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.callproc('multiply', (3, 5))
    except PostgreError:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        postgre_span = tracer.get_spans()[1]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) is ''
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == 'multiply'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'MULTIPLY'

        tracer.clear()
        connection.close()
