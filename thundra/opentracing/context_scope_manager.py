from __future__ import absolute_import

from contextlib import contextmanager
from contextvars import ContextVar

from opentracing import Scope, ScopeManager


_SCOPE = ContextVar('scope')


class ContextVarsScopeManager(ScopeManager):

    def activate(self, span, finish_on_close):
        return self._set_scope(span, finish_on_close)

    @property
    def active(self):
        return self._get_scope()

    def _set_scope(self, span, finish_on_close):
        return _ContextVarsScope(self, span, finish_on_close)

    def _get_scope(self):
        return _SCOPE.get(None)


class _ContextVarsScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(_ContextVarsScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        _SCOPE.set(self)

    def close(self):
        if self.manager.active is not self:
            return

        if self._finish_on_close:
            self.span.finish()


@contextmanager
def no_parent_scope():
    _SCOPE.set(None)
