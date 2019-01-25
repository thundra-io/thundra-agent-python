import abc

class SpanFilterer(abc.ABC):
    @abc.abstractmethod
    def accept(self, span):
        '''
        Returns whether or not given span is able to pass through
        the filterer.
        '''
class SpanFilter(abc.ABC):
    @abc.abstractmethod
    def accept(self, span):
        '''
        Returns whether or not given span is able to pass through
        the filter.
        '''

class ThundraSpanFilterer(SpanFilterer):
    
    def __init__(self, span_filters=[]):
        self.span_filters = span_filters

    def accept(self, span):
        for sf in self.span_filters:
            if sf.accept(span):
                return True
        return False

class ThundraSpanFilter(SpanFilter):
    
    def __init__(self,
                domain_name=None,
                class_name=None,
                operation_name=None,
                tags=None):
        self.domain_name = domain_name
        self.class_name = class_name
        self.operation_name = operation_name
        self.tags = tags
    
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
                if span.get_tag(k) != v:
                    accepted = False
                    break
        
        return accepted
