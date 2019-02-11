import uuid
from threading import Lock
import opentracing

from opentracing.scope_managers import ThreadLocalScopeManager
from thundra.opentracing.recorder import ThundraRecorder
from thundra.opentracing.span import ThundraSpan
from thundra.opentracing.span_context import ThundraSpanContext
from thundra.plugins.trace import trace_support

class ThundraTracer(opentracing.Tracer):
    __instance = None

    @staticmethod
    def get_instance():
        return ThundraTracer() if ThundraTracer.__instance is None else ThundraTracer.__instance

    def __init__(self, recorder=None, scope_manager=None):
        scope_manager = ThreadLocalScopeManager() if scope_manager is None else scope_manager
        super(ThundraTracer, self).__init__(scope_manager)
        self.recorder = recorder or ThundraRecorder()
        self.lock = Lock()
        self.global_span_order = 0
        ThundraTracer.__instance = self

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          trace_id=None,
                          transaction_id=None,
                          span_id=None,
                          parent_span_id=None,
                          tags=None,
                          start_time=None,
                          span_order=-1,
                          ignore_active_span=False,
                          finish_on_close=True):
        span_id = span_id or str(uuid.uuid4())
        _span = self.start_span(operation_name=operation_name,
                                child_of=child_of,
                                references=references,
                                trace_id=trace_id,
                                transaction_id=transaction_id,
                                span_id=span_id,
                                parent_span_id=parent_span_id,
                                tags=tags,
                                start_time=start_time,
                                span_order=span_order,
                                ignore_active_span=ignore_active_span)
        return self.scope_manager.activate(_span, finish_on_close)

    def start_span(self,
                   operation_name=None,
                   class_name=None,
                   domain_name=None,
                   child_of=None,
                   references=None,
                   trace_id=None,
                   transaction_id=None,
                   span_id=None,
                   parent_span_id=None,
                   tags=None,
                   start_time=None,
                   span_order=-1,
                   ignore_active_span=False):
        # Create a new span
        _span = self.create_span(operation_name=operation_name,
                                child_of=child_of,
                                references=references,
                                trace_id=trace_id,
                                transaction_id=transaction_id,
                                span_id=span_id,
                                parent_span_id=parent_span_id,
                                tags=tags,
                                start_time=start_time,
                                span_order=span_order,
                                ignore_active_span=ignore_active_span)
        # Record the new span
        self.recorder.record(_span)
        # Call listener's on_span_started method with the new span
        return _span

    def create_span(self,
                   operation_name=None,
                   class_name=None,
                   domain_name=None,
                   child_of=None,
                   references=None,
                   trace_id=None,
                   transaction_id=None,
                   span_id=None,
                   parent_span_id=None,
                   tags=None,
                   start_time=None,
                   span_order=-1,
                   ignore_active_span=False):
        
        with self.lock:
            self.global_span_order += 1

        _span_order = span_order
        if _span_order == -1:
            _span_order = self.global_span_order

        _parent_context = None
        if child_of is not None:
            _parent_context = child_of if isinstance(child_of, opentracing.SpanContext) else child_of.context
        elif references is not None and len(references) > 0:
            _parent_context = references[0].referenced_context

        if not ignore_active_span and _parent_context is None:
            _scope = self.scope_manager.active
            if _scope is not None and _scope.span is not None:
                _parent_context = _scope.span.context

        _trace_id = trace_id
        _transaction_id = transaction_id
        _span_id = span_id or str(uuid.uuid4())
        _parent_span_id = parent_span_id

        if _parent_context is not None:
            _trace_id = _trace_id or _parent_context.trace_id
            _transaction_id = _transaction_id or _parent_context.transaction_id
            _parent_span_id = _parent_span_id or _parent_context.span_id

        _context = ThundraSpanContext(trace_id=_trace_id,
                                      transaction_id=_transaction_id,
                                      span_id=_span_id,
                                      parent_span_id=_parent_span_id)
        _span = ThundraSpan(self,
                            operation_name=operation_name,
                            class_name=class_name,
                            domain_name=domain_name,
                            context=_context,
                            tags=tags,
                            start_time=start_time,
                            span_order=_span_order)

        return _span

    def get_active_span(self):
        scope = self.scope_manager.active
        if scope is not None:
            return scope.span
        
        return None

    def get_span_listeners(self):
        return trace_support.get_span_listeners()

    def get_spans(self):
        return self.recorder.get_spans()

    def inject(self, span_context, format, carrier):
        raise NotImplementedError('inject method not implemented yet')

    def extract(self, format, carrier):
        raise NotImplementedError('extract method not implemented yet')

    def clear(self):
        self.recorder.clear()

    def add_span_listener(self, listener):
        trace_support.register_span_listener(listener)
