import os
import pytest
from elasticsearch import Elasticsearch, ElasticsearchException

from thundra import constants
from thundra.opentracing.tracer import ThundraTracer


def test_create_index():
    try:
        es = Elasticsearch([{'host': 'test', 'port': 3737}], max_retries=0)
        
        author1 = {"name": "Sidney Sheldon", "novels_count": 18}

        es.index(index='authors', doc_type='authors', body=author1, id=1)
    except ElasticsearchException as e:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.class_name == constants.ClassNames['ELASTICSEARCH']
        assert span.domain_name == constants.DomainNames['DB']
        
        assert span.get_tag(constants.ESTags['ES_HOST']) == 'http://test'
        assert span.get_tag(constants.ESTags['ES_PORT']) == 3737
        assert span.get_tag(constants.ESTags['ES_METHOD']) == 'PUT'
        assert span.get_tag(constants.ESTags['ES_URI']) == '/authors/authors/1'
        assert span.get_tag(constants.ESTags['ES_BODY']) == author1

        assert span.get_tag(constants.DBTags['DB_TYPE']) == 'elasticsearch'
        assert span.get_tag(constants.DBTags['DB_HOST']) == 'http://test'
        assert span.get_tag(constants.DBTags['DB_PORT']) == 3737
        
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
        assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['']
        assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.LAMBDA_APPLICATION_DOMAIN_NAME
        assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.LAMBDA_APPLICATION_CLASS_NAME
        assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])

def test_mask_body(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_ES_BODY, 'true')
    try:
        es = Elasticsearch([{'host': 'test', 'port': 3737}], max_retries=0)
        
        INDEX_NAME = 'authors'
        author1 = {"name": "Sidney Sheldon", "novels_count": 18}

        es.index(index=INDEX_NAME, doc_type='authors', body=author1, id=1)
    except ElasticsearchException as e:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.get_tag(constants.ESTags['ES_BODY']) == None
