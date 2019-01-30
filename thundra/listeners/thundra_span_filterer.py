import abc
import thundra.utils as utils

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
            if hasattr(sf, 'accept'):
                if sf.accept(span):
                    return True
            else:
                raise TypeError("{} doesn't have accept method".format(type(sf)))
        return False
    
    def add_filter(self, filter):
        self.span_filters.append(filter)
    
    def clear_filters(self):
        self.span_filters.clear()

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

    def __repr__(self):
        return ("ThundraSpanFilter with class_name={}, domain_name={},",
            "operation_name={}, tags={}").format(self.class_name, self.domain_name, self.operation_name, self.tags)

    @staticmethod
    def from_config(config):
        kwargs = {}
        tags = {}
        domain_name = config.get('domainName')
        class_name = config.get('className')
        operation_name = config.get('operationName')

        tag_prefix = 'tag.'
        for k, v in config.items():
            if k.startswith(tag_prefix):
                tags[k[len(tag_prefix):]] = utils.str_to_proper_type(v)

        if domain_name is not None:
            kwargs['domain_name'] = str(domain_name)
        if class_name is not None:
            kwargs['class_name'] = str(class_name)
        if operation_name is not None:
            kwargs['operation_name'] = str(operation_name)
        if len(tags) > 0:
            kwargs['tags'] = tags
        

        return ThundraSpanFilter(**kwargs)