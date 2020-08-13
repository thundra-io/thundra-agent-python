from __future__ import absolute_import

from thundra import constants
from thundra.listeners.thundra_span_listener import ThundraSpanListener
from thundra.plugins.invocation import invocation_support

try:
    import builtins
except:
    import __builtin__ as builtins


class SecurityAwareSpanListener(ThundraSpanListener):
    def __init__(self, block=False, whitelist=None, blacklist=None):
        self.block = block
        self.whitelist = whitelist
        self.blacklist = blacklist

    def on_span_started(self, span):
        if not self.is_external_operation(span):
            return

        has_whitelist = isinstance(self.whitelist, list)
        has_blacklist = isinstance(self.blacklist, list)

        if has_blacklist:
            for op in self.blacklist:
                if op.matches(span):
                    self.handle_security_issue(span)
                    return

        if has_whitelist:
            for op in self.whitelist:
                if op.matches(span):
                    return

            self.handle_security_issue(span)

    def on_span_finished(self, span):
        pass

    @staticmethod
    def from_config(config):
        kwargs = {}
        kwargs['block'] = config.get('block')
        whitelist = config.get('whitelist', None)
        blacklist = config.get('blacklist', None)

        if isinstance(whitelist, list):
            kwargs['whitelist'] = list(map(Operation, whitelist))

        if isinstance(blacklist, list):
            kwargs['blacklist'] = list(map(Operation, blacklist))

        return SecurityAwareSpanListener(**kwargs)

    def is_external_operation(self, span):
        return span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX']) == True

    @staticmethod
    def should_raise_exceptions():
        return True

    def handle_security_issue(self, span):
        if self.block:
            err = SecurityError()
            span.set_tag(constants.SecurityTags['VIOLATED'], True)
            span.set_tag(constants.SecurityTags['BLOCKED'], True)
            span.set_error_to_tag(err)
            invocation_support.set_agent_tag(constants.SecurityTags['VIOLATED'], True)
            invocation_support.set_agent_tag(constants.SecurityTags['BLOCKED'], True)
            raise err
        else:
            span.set_tag(constants.SecurityTags['VIOLATED'], True)
            invocation_support.set_agent_tag(constants.SecurityTags['VIOLATED'], True)


class SecurityError(Exception):
    def __init__(self, msg='Operation was blocked due to security configuration'):
        super(Exception, self).__init__(msg)


class Operation:
    def __init__(self, config):
        self.class_name = config.get('className')
        self.operation_name = config.get('operationName')
        self.tags = config.get('tags')

    def matches(self, span):
        matched = self.class_name == span.class_name or self.class_name == '*'

        if matched and isinstance(self.operation_name, list):
            matched = span.operation_name in self.operation_name or '*' in self.operation_name

        if matched and self.tags:
            for k, v in self.tags.items():
                if isinstance(v, list):
                    if not (span.get_tag(k) in v or '*' in v):
                        matched = False
                        break
                elif span.get_tag(k) != v:
                    matched = False
                    break
        return matched
