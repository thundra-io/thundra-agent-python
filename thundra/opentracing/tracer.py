import uuid

import opentracing
from opentracing.scope_managers import ThreadLocalScopeManager
from thundra.opentracing.recorder import InMemoryRecorder, RecordEvents
from thundra.opentracing.span import ThundraSpan
from thundra.opentracing.span_context import ThundraSpanContext


class ThundraTracer(opentracing.Tracer):

    __instance = None

    @staticmethod
    def getInstance():
        return ThundraTracer() if ThundraTracer.__instance is None else ThundraTracer.__instance

    def __init__(self, recorder=None, scope_manager=None):
        scope_manager = ThreadLocalScopeManager() if scope_manager is None else scope_manager
        super(ThundraTracer, self).__init__(scope_manager)
        self.recorder = recorder or InMemoryRecorder()
        ThundraTracer.__instance = self

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          tags=None,
                          start_time=None,
                          ignore_active_span=False,
                          finish_on_close=True):
        span = self.start_span(
            operation_name=operation_name,
            child_of=child_of,
            references=references,
            tags=tags,
            start_time=start_time,
            ignore_active_span=ignore_active_span
        )

        return self.scope_manager.activate(span, finish_on_close)

    def start_span(self,
                   operation_name=None,
                   class_name=None,
                   domain_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None,
                   ignore_active_span=False):

        parent_context = None
        if child_of is not None:
            parent_context = child_of if isinstance(child_of, opentracing.SpanContext) else child_of.context
        elif references is not None and len(references) > 0:
            parent_context = references[0].referenced_context

        if not ignore_active_span and parent_context is None:
            scope = self.scope_manager.active
            if scope is not None and scope.span is not None:
                parent_context = scope.span.context

        parent_span_id = None
        trace_id = None
        if parent_context is not None:
            trace_id = parent_context.trace_id
            parent_span_id = parent_context.span_id

        trace_id = trace_id or str(uuid.uuid4())
        span = ThundraSpan(self,
                           operation_name=operation_name,
                           class_name=class_name,
                           domain_name=domain_name,
                           trace_id=trace_id,
                           tags=tags,
                           start_time=start_time)

        context = ThundraSpanContext(trace_id=trace_id, parent_span_id=parent_span_id, span_id=span.span_id)
        span.context = context

        self.recorder.record(RecordEvents.START_SPAN, span)
        return span

    def get_active_span(self):
        return self.recorder.get_active_span()

    def get_span_tree(self):
        return self.recorder.span_tree

    def record(self, event, span):
        self.recorder.record(event, span)

    def inject(self, span_context, format, carrier):
        raise NotImplemented('inject method not implemented yet')

    def extract(self, format, carrier):
        raise NotImplemented('extract method not implemented yet')
