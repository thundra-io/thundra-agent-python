import os
import redis
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer

def test_set():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.set('foo', 'bar')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'WRITE'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'SET'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == 'SET foo bar'
        tracer.clear()


def test_set_mask_command(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_REDIS_STATEMENT, 'true')
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.set('foo', 'bar')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'WRITE'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'SET'
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) == None
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == None
        
        tracer.clear()


def test_get():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'READ'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'GET'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == 'GET foo'
        tracer.clear()


def test_get_mask_command(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_REDIS_STATEMENT, 'true')

    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'redis'
        assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
        assert span.get_tag(constants.DBTags['DB_STATEMENT_TYPE']) == 'READ'
        assert span.get_tag(constants.RedisTags['REDIS_HOST']) == 'test'
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND_TYPE']) == 'GET'
        assert span.get_tag(constants.DBTags['DB_STATEMENT']) == None
        assert span.get_tag(constants.RedisTags['REDIS_COMMAND']) == None
        tracer.clear()
