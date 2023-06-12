import mysql.connector
from mysql.connector.errors import Error as MySQLError

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer


def test_mysql_integration():
    query = "SELECT 1 + 1 AS solution"
    connection = mysql.connector.connect(
        user='user',
        host='localhost',
        password='userpass',
        database='db', auth_plugin='mysql_native_password')

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        for table in cursor.fetchall():
            print(table)

    finally:
        tracer = CatchpointTracer.get_instance()
        mysql_span = tracer.get_spans()[1]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'

        connection.close()


def test_mysql_integration_mask_statement():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK, 'true')

    query = "SELECT 1 + 1 AS solution"
    connection = mysql.connector.connect(
        user='user',
        host='localhost',
        password='userpass',
        database='db', auth_plugin='mysql_native_password')

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        for table in cursor.fetchall():
            print(table)

    finally:
        tracer = CatchpointTracer.get_instance()
        mysql_span = tracer.get_spans()[1]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == None
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'

        connection.close()


def test_mysql_integration_with_empty_query():
    connection = mysql.connector.connect(
        user='user',
        host='localhost',
        password='userpass',
        database='db', auth_plugin='mysql_native_password')

    try:
        cursor = connection.cursor()
        cursor.execute('')
        for table in cursor.fetchall():
            print(table)
    except MySQLError:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        mysql_span = tracer.get_spans()[1]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == ''
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == ''
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == ''

        connection.close()


def test_mysql_integration_callproc():
    connection = mysql.connector.connect(
        user='user',
        host='localhost',
        password='userpass',
        database='db', auth_plugin='mysql_native_password')

    try:
        cursor = connection.cursor()
        cursor.callproc('multiply')
    except MySQLError:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        mysql_span = tracer.get_spans()[1]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == ''
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == 'multiply'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'MULTIPLY'

        connection.close()
