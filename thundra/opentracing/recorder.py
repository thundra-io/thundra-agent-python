from threading import Lock, local


class RecordEvents:
    START_SPAN = 'start_span'
    FINISH_SPAN = 'finish_span'


class Node:
    def __init__(self, key):
        self._key = key
        self._children = []

    @property
    def key(self):
        return self._key

    @property
    def children(self):
        return self._children

    def add_child(self, key):
        self._children.append(key)

class InMemoryRecorder:
    def __init__(self):
        self._lock = Lock()
        self._active_span_stack = []
        self._span_tree = None
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes

    @property
    def span_tree(self):
        return self._span_tree

    @property
    def active_span_stack(self):
        return self._active_span_stack

    def get_active_span(self):
        if self._active_span_stack is not None and len(self._active_span_stack) > 0:
            return self._active_span_stack[-1].key
        return None

    def record(self, event, span):
        with self._lock:
            if event == RecordEvents.START_SPAN:
                self._record_start_span(span)
            elif event == RecordEvents.FINISH_SPAN:
                self._record_finish_span()

    def _record_start_span(self, span):
        node = Node(span)
        self._add_span(node)
        self._active_span_stack.append(node)

    def _record_finish_span(self):
        if len(self._active_span_stack) > 0:
            self._active_span_stack.pop()

    def _add_span(self, span):
        parent_span_id = span.key.context.parent_span_id
        if parent_span_id is not None:
            for key in self.nodes:
                if key.span_id == parent_span_id:
                    parent_node = self.nodes[key]
                    parent_node.add_child(span)
        elif self._active_span_stack is not None:
            if len(self._active_span_stack) == 0:
                self._span_tree = span
                self.nodes[span.key] = span
                return
            if len(self._active_span_stack) > 0:
                parent_node = self._active_span_stack[-1]
                parent_node.add_child(span)
        self.nodes[span.key] = span



