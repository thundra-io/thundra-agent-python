
import psycopg2

from thundra.opentracing.tracer import ThundraTracer
from thundra import constants


def test_postgre_integration():
    query = "select 1 + 1 AS solution"

    connection =  psycopg2.connect(
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
        tracer = ThundraTracer.get_instance()
        postgre_span = tracer.recorder.finished_span_stack[0]

        assert postgre_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['RDB']
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag( constants.SpanTags['DB_URL']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query.lower()
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'AWS-Lambda'
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'API'

        tracer.clear()
        connection.close()