import logging

from thundra import config, constants
from thundra.opentracing.tracer import ThundraTracer


logger = logging.getLogger(__name__)
class Resource:

    def __init__(self, span):
        self.type = span.class_name.upper()
        self.name = span.operation_name
        self.operation = str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        self.count = 1
        self.error_count = 1 if span.errorneous() else 0
        self.error_types = set([span.get_tag('error.kind')]) if span.errorneous() else set()
        self.duration = span.get_duration()
    
    def accept(self, span):
        return (
            self.type == span.class_name.upper() and
            self.name == span.operation_name and
            self.operation == str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        )
    
    def merge(self, span):
        if not self.accept(span):
            logger.error(("can not merge resource with id %s:"
                " ids not match with target resource"), resource_id(span))
            return
        self.count += 1
        self.duration += span.get_duration()
        errorneous = span.errorneous()
        if errorneous:
            self.error_count += 1
            self.error_types.add(span.get_tag('error.kind'))
    
    def to_dict(self):
        return {
            'resourceType': self.type,
            'resourceName': self.name,
            'resourceOperation': self.operation,
            'resourceCount': self.count,
            'resourceErrorCount': self.error_count,
            'resourceDuration': self.duration,
            'resourceErrors': list(self.error_types)
        }


def resource_id(span):
    return ('{}${}${}'.format(
        span.class_name.upper(),
        span.operation_name,
        str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
    ))

def get_resources():
    try:
        resources = {}
        spans = ThundraTracer.get_instance().recorder.get_spans()
        for span in spans:
            if not span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX']):
                continue
            rid = resource_id(span)
            if not rid in resources:
                resources[rid] = Resource(span)
            else:
                resources[rid].merge(span)
        return {
            'resources': [r.to_dict() for r in resources.values()]
        }
    except Exception as e:
        logger.error("error while creating the resources data for invocation: %s", e)
        return {}
