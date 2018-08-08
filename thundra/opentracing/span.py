import time
import uuid
from threading import Lock

import opentracing
from thundra.opentracing.recorder import RecordEvents


class ThundraSpan(opentracing.Span):
    def __init__(self,
                 tracer,
                 operation_name=None,
                 class_name=None,
                 domain_name=None,
                 context=None,
                 trace_id=None,
                 span_id=None,
                 tags=None,
                 start_time=None):
        super(ThundraSpan, self).__init__(tracer, context)
        self._tracer = tracer
        self._context = context
        self._lock = Lock()

        self.trace_id = trace_id
        self.span_id = span_id or str(uuid.uuid4())
        self.operation_name = operation_name
        self.class_name = class_name
        self.domain_name = domain_name
        self.start_time = start_time or int(time.time() * 1000)
        self.tags = tags if tags is not None else {}
        self.duration = -1
        self.logs = []

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

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
        return self.tags.get(key)

    def finish(self, f_time=None):
        with self._lock:
            finish_time = int(time.time() * 1000) if f_time is None else f_time
            self.duration = finish_time - self.start_time
            self._tracer.record(RecordEvents.FINISH_SPAN, self)

    def log_kv(self, key_values, timestamp=None):
        with self._lock:
            log = key_values
            log['timestamp'] = timestamp
            self.logs.append(log)
        return super(ThundraSpan, self).log_kv(key_values, timestamp)

    def set_baggage_item(self, key, value):
        new_context = self.context.context_with_baggage_item(key, value)
        with self._lock:
            self.context = new_context
        return self

    def get_baggage_item(self, key):
        with self._lock:
            return self.context.baggage.get(key)

    def set_error_to_tag(self, err):
        error_type = type(err)
        self.set_tag('error', True)
        self.set_tag('error.kind', error_type.__name__)
        self.set_tag('error.message', str(err))
