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
        # print(vars(span))
        assert span.className == 'Redis'
        assert span.domainName == 'Cache'
        assert span.operationName == 'test'
        assert span.get_tag('db.type') == 'redis'
        assert span.get_tag('db.instance') == 'test:12345'
        assert span.get_tag('db.statement.type') == 'WRITE'
        assert span.get_tag('redis.host') == 'test:12345'
        assert span.get_tag('redis.command.type') == 'SET'
        assert span.get_tag('redis.command') == 'WRITE'
        assert span.get_tag('redis.command.args') == ['foo', 'bar']

def test_get():
    try:
        r = redis.Redis(host="test", port="12345", password="pass")
        r.get('foo')
    except:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.recorder.finished_span_stack[-1]
        assert span.className == 'Redis'
        assert span.domainName == 'Cache'
        assert span.operationName == 'test'
        assert span.get_tag('db.type') == 'redis'
        assert span.get_tag('db.instance') == 'test:12345'
        assert span.get_tag('db.statement.type') == 'READ'
        assert span.get_tag('redis.host') == 'test:12345'
        assert span.get_tag('redis.command.type') == 'GET'
        assert span.get_tag('redis.command') == 'READ'
        assert span.get_tag('redis.command.args') == ['foo']