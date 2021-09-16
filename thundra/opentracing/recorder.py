import copy
from threading import Lock


class ThundraRecorder:

    def __init__(self):
        self._lock = Lock()
        self._spans = []
        self.index = 0 # Added for foresight do not use for other utilities

    def record(self, span):
        with self._lock:
            self.index += 1
            self._spans.append(span)

    def get_spans(self):
        return copy.copy(self._spans)


    def get_current_span(self): # Added for foresight do not use for other utilities
        with self._lock:
            if self.index > 0 and len(self._spans) > 0:
                current_span = self._spans[self.index]
                self.index -= 1
                return current_span
            return None
        

    def clear(self):
        self._spans = []
