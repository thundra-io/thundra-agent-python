import abc

ABC = abc.ABCMeta('ABC', (object,), {})


class SpanFilterer(ABC):
    @abc.abstractmethod
    def accept(self, span):
        """
        Returns whether or not given span is able to pass through
        the filterer.
        """


class SpanFilter(ABC):
    @abc.abstractmethod
    def accept(self, span):
        """
        Returns whether or not given span is able to pass through
        the filter.
        """


class StandardSpanFilterer(SpanFilterer):

    def __init__(self, span_filters=None, all_mandatory=False):
        if span_filters is None:
            span_filters = []
        self.span_filters = span_filters
        self.all_mandatory = all_mandatory

    def accept(self, span):
        if (not self.span_filters) or len(self.span_filters) == 0:
            return True

        if self.all_mandatory:
            for sf in self.span_filters:
                if hasattr(sf, 'accept'):
                    if not sf.accept(span):
                        return False
                else:
                    raise TypeError("{} doesn't have accept method".format(type(sf)))
            return True

        else:
            for sf in self.span_filters:
                if hasattr(sf, 'accept'):
                    if sf.accept(span):
                        return True
                else:
                    raise TypeError("{} doesn't have accept method".format(type(sf)))
            return False

    def add_filter(self, span_filter):
        self.span_filters.append(span_filter)

    def clear_filters(self):
        self.span_filters = []


class SimpleSpanFilter(SpanFilter):

    def __init__(self,
                 domain_name=None,
                 class_name=None,
                 operation_name=None,
                 tags=None, reverse=False):
        self.domain_name = domain_name
        self.class_name = class_name
        self.operation_name = operation_name
        self.tags = tags
        self.reverse = reverse

    def accept(self, span):
        accepted = True
        if self.domain_name is not None:
            accepted = self.domain_name == span.domain_name

        if accepted and self.class_name is not None:
            accepted = self.class_name == span.class_name

        if accepted and self.operation_name is not None:
            accepted = self.operation_name == span.operation_name

        if accepted and self.tags is not None:
            for k, v in self.tags.items():
                if isinstance(v, list):
                    if not (span.get_tag(k) in v):
                        accepted = False
                        break
                elif span.get_tag(k) != v:
                    accepted = False
                    break
        if self.reverse:
            accepted = not accepted

        return accepted

    def __repr__(self):
        return ("SpanFilter with class_name={}, domain_name={}," +
                "operation_name={}, tags={}, reverse={}").format(self.class_name, self.domain_name, self.operation_name,
                                                                 self.tags, self.reverse)

    @staticmethod
    def from_config(config):
        kwargs = {}
        tags = config.get('tags')
        domain_name = config.get('domainName')
        class_name = config.get('className')
        operation_name = config.get('operationName')
        reverse = config.get('reverse')

        if domain_name is not None:
            kwargs['domain_name'] = str(domain_name)
        if class_name is not None:
            kwargs['class_name'] = str(class_name)
        if operation_name is not None:
            kwargs['operation_name'] = str(operation_name)
        if reverse is not None:
            kwargs['reverse'] = reverse
        if len(tags) > 0:
            kwargs['tags'] = tags

        return SimpleSpanFilter(**kwargs)
