from __future__ import division

import logging

from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.context.execution_context_manager import ExecutionContextManager

logger = logging.getLogger(__name__)


class Resource:

    def __init__(self, span):
        self.type = span.class_name
        self.name = span.operation_name
        self.operation = str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        self.count = 1
        self.error_count = 1 if span.erroneous() else 0
        self.security_violated_count = 1 if span.get_tag(constants.SecurityTags['VIOLATED']) else 0
        self.security_blocked_count = 1 if span.get_tag(constants.SecurityTags['BLOCKED']) else 0
        self.error_types = {span.get_tag('error.kind')} if span.erroneous() else set()
        self.duration = span.get_duration()
        self.resource_max_duration = self.duration
        self.resource_trace_links = set()
        if hasattr(span, 'resource_trace_links') and hasattr(span.resource_trace_links, '__iter__'):
            self.resource_trace_links = set(span.resource_trace_links)

    def accept(self, span):
        return (
                self.type.upper() == span.class_name.upper() and
                self.name == span.operation_name and
                self.operation == str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        )

    def merge(self, span):
        if not self.accept(span):
            logger.error(("can not merge resource with id %s:"
                          " ids not match with target resource"), _resource_id(span))
            return
        self.count += 1
        self.duration += span.get_duration()
        errorneous = span.erroneous()

        if span.get_tag(constants.SecurityTags['VIOLATED']):
            self.security_violated_count += 1

        if span.get_tag(constants.SecurityTags['BLOCKED']):
            self.security_blocked_count += 1

        if errorneous:
            self.error_count += 1
            self.error_types.add(span.get_tag('error.kind'))

        if span.get_duration() > self.resource_max_duration:
            self.resource_max_duration = span.get_duration()

        if self.resource_trace_links and hasattr(span, 'resource_trace_links') and hasattr(span.resource_trace_links,
                                                                                           '__iter__'):
            self.resource_trace_links.update(span.resource_trace_links)

    def to_dict(self):
        resource = {
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
        if self.resource_trace_links:
            resource['resourceTraceLinks'] = list(self.resource_trace_links)
        return resource


def _resource_id(span, resource_name=None):
    if resource_name:
        return ('{}${}${}'.format(
            span.class_name.upper(),
            resource_name,
            str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
        ))
    return ('{}${}${}'.format(
        span.class_name.upper(),
        span.operation_name,
        str(span.get_tag(constants.SpanTags['OPERATION_TYPE']))
    ))


def get_resources():
    try:
        resources = {}
        execution_context = ExecutionContextManager.get()
        spans = execution_context.recorder.get_spans()
        root_span_id = execution_context.root_span.context.span_id
        for span in spans:
            if (not span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])
                    or span.span_id == root_span_id):
                continue

            resource_names = span.get_tag(constants.SpanTags['RESOURCE_NAMES'])
            if resource_names:
                for resource_name in resource_names:
                    rid = _resource_id(span, resource_name)
                    if rid:
                        if not rid in resources:
                            resources[rid] = Resource(span)
                            resources[rid].name = resource_name
                        else:
                            resources[rid].merge(span)
            else:
                rid = _resource_id(span)
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
    if ConfigProvider.get(config_names.THUNDRA_DISABLE, False):
        return {}

    execution_context = ExecutionContextManager.get()
    incoming_trace_links = list(set(execution_context.incoming_trace_links))[:constants.MAX_INCOMING_TRACE_LINKS]
    return {"incomingTraceLinks": incoming_trace_links}


def get_outgoing_trace_links():
    if ConfigProvider.get(config_names.THUNDRA_DISABLE, False):
        return {}

    execution_context = ExecutionContextManager.get()
    spans = execution_context.recorder.get_spans()

    outgoing_trace_links = []
    outgoing_trace_links.extend(execution_context.outgoing_trace_links)
    for span in spans:
        links = get_outgoing_trace_link(span)
        if links:
            outgoing_trace_links += links

    outgoing_trace_links = list(set(outgoing_trace_links))[:constants.MAX_OUTGOING_TRACE_LINKS]
    return {"outgoingTraceLinks": outgoing_trace_links}


def add_outgoing_trace_link(trace_link):
    execution_context = ExecutionContextManager.get()
    execution_context.outgoing_trace_links.append(trace_link)


def add_outgoing_trace_links(trace_links):
    execution_context = ExecutionContextManager.get()
    execution_context.outgoing_trace_links.extend(trace_links)


def get_outgoing_trace_link(span):
    return span.get_tag(constants.SpanTags["TRACE_LINKS"])


def add_incoming_trace_link(trace_link):
    execution_context = ExecutionContextManager.get()
    execution_context.incoming_trace_links.extend(trace_link)


def add_incoming_trace_links(trace_links):
    execution_context = ExecutionContextManager.get()
    execution_context.incoming_trace_links.extend(trace_links)
