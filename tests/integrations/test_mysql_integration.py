
import mysql.connector

from thundra.opentracing.tracer import ThundraTracer
from thundra import constants



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
        mysql_span = tracer.recorder.finished_span_stack[0]

        assert mysql_span.operation_name == 'db'
        assert mysql_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['RDB']
        assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert mysql_span.get_tag(constants.SpanTags['DB_URL']) == 'localhost'
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query.lower()
        assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'AWS-Lambda'
        assert mysql_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'API'

        tracer.clear()
        connection.close()