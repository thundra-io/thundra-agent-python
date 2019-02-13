import time
import opentracing
import logging
from threading import Lock


logger = logging.getLogger(__name__)

class ThundraSpan(opentracing.Span):

    def __init__(self,
                 tracer,
                 operation_name=None,
                 class_name=None,
                 domain_name=None,
                 context=None,
                 tags=None,
                 start_time=None,
                 span_order=-1):
        super(ThundraSpan, self).__init__(tracer, context)
        self._tracer = tracer
        self._context = context
        self._lock = Lock()
        self.operation_name = operation_name if operation_name is not None else ""
        self.class_name = class_name if class_name is not None else ""
        self.domain_name = domain_name if domain_name is not None else ""
        self.start_time = start_time or int(time.time() * 1000)
        self.finish_time = 0
        self.span_order = span_order
        self.tags = tags if tags is not None else {}
        self.logs = []

    @property
    def context(self):
        return self._context

    @property
    def trace_id(self):
        return self._context.trace_id

    @property
    def transaction_id(self):
        return self._context.transaction_id

    @property
    def span_id(self):
        return self._context.span_id

    def set_operation_name(self, operation_name):
        with self._lock:
            self.operation_name = operation_name
        return super(ThundraSpan, self).set_operation_name(operation_name)

    def set_tag(self, key, value):
        with self._lock:
            if self.tags is None:
                self.tags = {}
            self.tags[key] = value
        return super(ThundraSpan, self).set_tag(key, value)

    def get_tag(self, key):
        if self.tags is not None:
            return self.tags.get(key)
        return None

    def finish(self, f_time=None):
        with self._lock:
            self.finish_time = int(time.time() * 1000) if f_time is None else f_time
        self.on_finished()
        
    def on_finished(self):
        span_listeners = self._tracer.get_span_listeners()
        for sl in span_listeners:
            try:
                sl.on_span_finished(self)
            except Exception as e:
                if not sl.should_raise_exceptions():
                    logger.error(("error while calling"
                        " on_finished of %s: %s"), type(sl), e)
                else:
                    raise e
    
    def on_started(self):
        span_listeners = self._tracer.get_span_listeners()
        for sl in span_listeners:
            try:
                sl.on_span_started(self)
            except Exception as e:
                if not sl.should_raise_exceptions():
                    logger.error(("error while calling"
                        " on_started of %s: %s"), type(sl), e)
                else:
                    raise e

    def log_kv(self, key_values, timestamp=None):
        with self._lock:
            log = key_values
            log['timestamp'] = timestamp
            self.logs.append(log)
        return super(ThundraSpan, self).log_kv(key_values, timestamp)

    def set_baggage_item(self, key, value):
        new_context = self.context.context_with_baggage_item(key, value)
        with self._lock:
            self._context = new_context
        return self

    def get_baggage_item(self, key):
        with self._lock:
            return self.context.baggage.get(key)

    def set_error_to_tag(self, err):
        error_type = type(err)
        self.set_tag('error', True)
        self.set_tag('error.kind', error_type.__name__)
        self.set_tag('error.message', str(err))

    def get_duration(self):
        if self.finish_time == 0:
            return int(time.time() * 1000) - self.start_time
        else:
            return self.finish_time - self.start_time
    
    def errorneous(self):
        return self.tags is not None and 'error' in self.tags
