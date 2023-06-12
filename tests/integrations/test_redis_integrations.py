import redis

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer


def test_set():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.set('foo', 'bar')
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'WRITE'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'SET'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == 'SET foo bar'


def test_set_mask_command():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK, 'true')

    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.set('foo', 'bar')
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'WRITE'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'SET'
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) is None


def test_get():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'READ'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'GET'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == 'GET foo'


def test_get_mask_command():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK, 'true')

    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'READ'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'GET'
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) is None
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) is None
        tracer.clear()
