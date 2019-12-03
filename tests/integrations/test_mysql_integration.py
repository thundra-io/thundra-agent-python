import os
import mysql.connector
from mysql.connector.errors import Error as MySQLError
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer
from thundra.config import utils
property_accessor = utils.get_property_accessor()

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
        tracer = ThundraTracer.get_instance()
        mysql_span = tracer.get_spans()[0]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-Lambda'

        tracer.clear()
        connection.close()

def test_mysql_integration_mask_statement(monkeypatch):
    monkeypatch.setitem(property_accessor.props, constants.THUNDRA_MASK_RDB_STATEMENT, 'true')

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
        tracer = ThundraTracer.get_instance()
        mysql_span = tracer.get_spans()[0]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == None
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-Lambda'

        tracer.clear()
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
        tracer = ThundraTracer.get_instance()
        mysql_span = tracer.get_spans()[0]

        assert mysql_span.domain_name == constants.DomainNames['DB']
        assert mysql_span.class_name == constants.ClassNames['MYSQL']
        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == ''
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == ''
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == ''
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-Lambda'

        tracer.clear()
        connection.close()