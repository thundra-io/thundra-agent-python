import copy
from threading import Lock


class ThundraRecorder:

    def __init__(self):
        self._lock = Lock()
        self._spans = []

    def record(self, span):
        with self._lock:
            self._spans.append(span)

    def get_spans(self):
        return copy.copy(self._spans)

    def clear(self):
        self._spans = []
