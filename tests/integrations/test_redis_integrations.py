from thundra.opentracing.tracer import ThundraTracer
import redis


def test_set():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.set('foo', 'bar')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag('db.type') == 'redis'
        assert span.get_tag('db.instance') == 'test'
        assert span.get_tag('db.statement.type') == 'WRITE'
        assert span.get_tag('redis.host') == 'test'
        assert span.get_tag('redis.command.type') == 'SET'
        assert span.get_tag('redis.command') == 'SET foo bar'
        tracer.clear()


def test_get():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        assert span.class_name == 'Redis'
        assert span.domain_name == 'Cache'
        assert span.operation_name == 'test'
        assert span.get_tag('db.type') == 'redis'
        assert span.get_tag('db.instance') == 'test'
        assert span.get_tag('db.statement.type') == 'READ'
        assert span.get_tag('redis.host') == 'test'
        assert span.get_tag('redis.command.type') == 'GET'
        assert span.get_tag('redis.command') == 'GET foo'
        tracer.clear()