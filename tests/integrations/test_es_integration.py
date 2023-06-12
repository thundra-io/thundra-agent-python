from elasticsearch import Elasticsearch, ElasticsearchException

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer


def test_create_index():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH, '3')
    author1 = {"name": "Sidney Sheldon", "novels_count": 18}
    try:
        es = Elasticsearch([{'host': 'test', 'port': 3737}], max_retries=0)
        es.index(index='authors', doc_type='authors', body=author1, id=1)
    except ElasticsearchException as e:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.operation_name == '/authors/authors/1'
        assert span.class_name == constants.ClassNames['ELASTICSEARCH']
        assert span.domain_name == constants.DomainNames['DB']

        assert span.get_tag(constants.ESTags['ES_HOSTS']) == ['http://test:3737']
        assert span.get_tag(constants.ESTags['ES_URI']) == '/authors/authors/1'
        assert span.get_tag(constants.ESTags['ES_BODY']) == author1

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'elasticsearch'

        assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])


def test_get_doc():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH, '3')
    try:
        es = Elasticsearch(['one_host', 'another_host'], max_retries=0)
        es.get(index='test-index', doc_type='tweet', id=1)
    except ElasticsearchException as e:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        hosts = span.get_tag(constants.ESTags['ES_HOSTS'])

        assert span.operation_name == '/test-index/tweet/1'
        assert span.class_name == constants.ClassNames['ELASTICSEARCH']
        assert span.domain_name == constants.DomainNames['DB']

        assert len(hosts) == 2
        assert 'http://one_host:9200' in hosts
        assert 'http://another_host:9200' in hosts
        assert span.get_tag(constants.ESTags['ES_METHOD']) == 'GET'
        assert span.get_tag(constants.ESTags['ES_URI']) == '/test-index/tweet/1'
        assert span.get_tag(constants.ESTags['ES_BODY']) == {}

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'elasticsearch'

        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'GET'
        assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])


def test_refresh():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH, '2')
    try:
        es = Elasticsearch([{'host': 'test', 'port': 3737}], max_retries=0)
        res = es.indices.refresh(index='test-index')
        print(res)
    except ElasticsearchException as e:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.operation_name == '/test-index/_refresh'
        assert span.class_name == constants.ClassNames['ELASTICSEARCH']
        assert span.domain_name == constants.DomainNames['DB']

        assert span.get_tag(constants.ESTags['ES_HOSTS']) == ['http://test:3737']
        assert span.get_tag(constants.ESTags['ES_URI']) == '/test-index/_refresh'
        assert span.get_tag(constants.ESTags['ES_BODY']) == {}

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'elasticsearch'

        assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])


def test_mask_body():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_BODY_MASK, 'true')
    try:
        es = Elasticsearch([{'host': 'test', 'port': 3737}], max_retries=0)
        author1 = {"name": "Sidney Sheldon", "novels_count": 18}
        es.index(index='authors', doc_type='authors', body=author1, id=1)
    except ElasticsearchException:
        pass
    finally:
        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[1]

        assert span.get_tag(constants.ESTags['ES_BODY']) is None
