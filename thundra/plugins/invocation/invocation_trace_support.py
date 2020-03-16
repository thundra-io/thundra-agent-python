from __future__ import division
import logging

from thundra import config, constants
from thundra.opentracing.tracer import ThundraTracer

_incoming_trace_links = []

logger = logging.getLogger(__name__)
class Resource:

    def __init__(self, span):
        self.type = span.class_name
        self.name = span.operation_name
        self.operation = str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        self.count = 1
        self.error_count = 1 if span.errorneous() else 0
        self.security_violated_count = 1 if span.get_tag(constants.SecurityTags['VIOLATED']) else 0
        self.security_blocked_count = 1 if span.get_tag(constants.SecurityTags['BLOCKED']) else 0
        self.error_types = set([span.get_tag('error.kind')]) if span.errorneous() else set()
        self.duration = span.get_duration()
        self.resource_max_duration = self.duration
    
    def accept(self, span):
        return (
            self.type.upper() == span.class_name.upper() and
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

        if span.get_tag(constants.SecurityTags['VIOLATED']):
            self.security_violated_count += 1

        if span.get_tag(constants.SecurityTags['BLOCKED']):
            self.security_blocked_count += 1

        if errorneous:
            self.error_count += 1
            self.error_types.add(span.get_tag('error.kind'))

        if span.get_duration() > self.resource_max_duration:
            self.resource_max_duration = span.get_duration()

    def to_dict(self):
        return {
            'resourceType': self.type,
            'resourceName': self.name,
            'resourceOperation': self.operation,
            'resourceCount': self.count,
            'resourceErrorCount': self.error_count,
            'resourceViolatedCount': self.security_violated_count,
            'resourceBlockedCount': self.security_blocked_count,            
            'resourceDuration': self.duration,
            'resourceErrors': list(self.error_types),
            'resourceMaxDuration': self.resource_max_duration,
            'resourceAvgDuration': self.duration / self.count
        }


def resource_id(span, resource_name=None):
    if resource_name:
        return  ('{}${}${}'.format(
            span.class_name.upper(),
            resource_name,
            str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        ))
    return ('{}${}${}'.format(
        span.class_name.upper(),
        span.operation_name,
        str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
    ))


def get_resources(plugin_context):
    try:
        resources = {}
        root_span_id = plugin_context.get('span_id', '')
        spans = ThundraTracer.get_instance().recorder.get_spans()
        for span in spans:
            if (not span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
                or span.span_id == root_span_id):
                continue

            resource_names = span.get_tag(constants.SpanTags['RESOURCE_NAMES'])
            if resource_names:
                for resource_name in resource_names:
                    rid = resource_id(span, resource_name)
                    if rid:
                        if not rid in resources:
                            resources[rid] = Resource(span)
                            resources[rid].name = resource_name
                        else:
                            resources[rid].merge(span)
            else:
                rid = resource_id(span)
                if rid:
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

def get_incoming_trace_links():
    if config.thundra_disabled():
        return []
    
    return {"incomingTraceLinks": list(set(_incoming_trace_links))}
    

def get_outgoing_trace_links():
    if config.thundra_disabled():
        return []
    
    spans = ThundraTracer.get_instance().recorder.get_spans()

    outgoing_trace_links = []
    for span in spans:
        links = get_outgoing_trace_link(span)
        if links:
            outgoing_trace_links += links
    
    return {"outgoingTraceLinks": list(set(outgoing_trace_links))}

def get_outgoing_trace_link(span):
    return span.get_tag(constants.SpanTags["TRACE_LINKS"])

def add_incoming_trace_links(trace_links):
    _incoming_trace_links.extend(trace_links)


def clear():
    global _incoming_trace_links
    _incoming_trace_links = []