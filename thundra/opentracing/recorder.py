from threading import Lock, local


class RecordEvents:
    START_SPAN = 'start_span'
    FINISH_SPAN = 'finish_span'


class InMemoryRecorder:
    def __init__(self):
        self._lock = Lock()
        self._active_span_stack = []

    @property
    def active_span_stack(self):
        return self._active_span_stack

    def get_active_span(self):
        if self._active_span_stack is not None and len(self._active_span_stack) > 0:
            return self._active_span_stack[-1]
        return None

    def get_root_span(self):
        if self._active_span_stack is not None and len(self._active_span_stack) > 0:
            return self._active_span_stack[0]
        return None

    def record(self, event, span):
        with self._lock:
            if event == RecordEvents.START_SPAN:
                self._record_start_span(span)
            elif event == RecordEvents.FINISH_SPAN:
                self._record_finish_span()

    def _record_start_span(self, span):
        self._active_span_stack.append(span)

    def _record_finish_span(self):
        if len(self._active_span_stack) > 0:
            self._active_span_stack.pop()



