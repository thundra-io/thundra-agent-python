from thundra.listeners.thundra_span_filterer import SpanFilter


class CompositeSpanFilter(SpanFilter):
    
    def __init__(self, is_all=False, filters=[]):
        self.all = is_all
        self.filters = filters

    def accept(self, span):
        if (not self.filters) or len(self.filters) == 0:
            return True

        result = self.all

        if self.all:
            for span_filter in self.filters:
                result = result and span_filter.accept(span)
        else:
            for span_filter in self.filters:
                result = result or span_filter.accept(span)
        return result
    
    def set_filters(self, filters):
        self.filters = filters