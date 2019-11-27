from __future__ import absolute_import
import logging
from threading import Lock
from importlib import import_module
from thundra import constants, utils
from thundra.listeners.thundra_span_listener import ThundraSpanListener

logger = logging.getLogger(__name__)

try:
    import builtins
except:
    import __builtin__ as builtins


class TagInjectorSpanListener(ThundraSpanListener):
    def __init__(self, inject_on_finish=False, tags_to_inject=None):
        self.inject_on_finish = inject_on_finish
        self.tags_to_inject = tags_to_inject

    def on_span_started(self, span):
        if not self.inject_on_finish:
            self._inject_tags(span)

    def on_span_finished(self, span):
        if self.inject_on_finish:
            self._inject_tags(span)

    def _inject_tags(self, span):
        if self.tags_to_inject:
            for tag in self.tags_to_inject:
                span.set_tag(tag, self.tags_to_inject.get(tag))

    @staticmethod
    def from_config(config):
        kwargs = {}
        inject_on_finish = config.get('injectOnFinish')
        tags_to_inject = config.get('tags')
        if inject_on_finish != None:
            kwargs['inject_on_finish'] = inject_on_finish
        if tags_to_inject != None:
            kwargs['tags_to_inject'] = tags_to_inject

        return TagInjectorSpanListener(**kwargs)
    
    @staticmethod
    def should_raise_exceptions():
        return False
