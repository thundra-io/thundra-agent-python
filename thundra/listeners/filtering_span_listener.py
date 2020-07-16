import logging
from thundra.listeners import ThundraSpanListener
from thundra.listeners.thundra_span_filterer import SimpleSpanFilter, SpanFilterer
from thundra.listeners.thundra_span_filterer import StandardSpanFilterer
from thundra.listeners.composite_span_filter import CompositeSpanFilter

logger = logging.getLogger(__name__)

class FilteringSpanListener(ThundraSpanListener):
    
    def __init__(self, listener=None, filterer=None):
        self.listener = listener
        self.filterer = filterer

    def on_span_started(self, span):
        if self.listener is None:
            return
        if self.filterer is None or self.filterer.accept(span):
            self.listener.on_span_started(span)
    
    def on_span_finished(self, span):
        if self.listener is None:
            return
        if self.filterer is None or self.filterer.accept(span):
            self.listener.on_span_finished(span)
    
    @staticmethod
    def should_raise_exceptions():
        return True

    @staticmethod
    def from_config(config):
        listener = FilteringSpanListener._get_span_listener_from_config(config)
        filterer = FilteringSpanListener._get_span_filterer_from_config(config)
        return FilteringSpanListener(listener=listener, filterer=filterer)

    @staticmethod
    def _get_span_filters_from_config(config):
        span_filters = []
        is_all = config.get('all', False)
        if not config.get('filters'):
            return StandardSpanFilterer(span_filters=[], all_mandatory=is_all)
        for filter_config in config.get('filters'):
            composite = filter_config.get('composite')
            if composite:
                composite_filter = CompositeSpanFilter(is_all=filter_config.get('all', False))
                filters = FilteringSpanListener._get_span_filters_from_config(filter_config)
                composite_filter.set_filters(filters)
                span_filters.append(composite_filter)
            else:
                span_filters.append(SimpleSpanFilter(
                    filter_config.get('domainName'),
                    filter_config.get('className'),
                    filter_config.get('operationName'),
                    filter_config.get('tags'),
                    filter_config.get('reverse')
                ))
        
        return span_filters

    @staticmethod
    def _get_span_filterer_from_config(config):
        SPAN_FILTERERS= {
            sl_class.__name__: sl_class 
            for sl_class in SpanFilterer.__subclasses__()
        }
        is_all = config.get('all', False)

        filterer_class = None
        if 'filterer' in config:
            try:
                filterer_class_name = config.get("filterer")
                filterer_class = SPAN_FILTERERS[filterer_class_name]
            except KeyError:
                filterer_class = None
                logger.error('given span listener class %s is not found', filterer_class)
                return None
        else:
            filterer_class = StandardSpanFilterer
        span_filters = FilteringSpanListener._get_span_filters_from_config(config)
        return filterer_class(span_filters=span_filters, all_mandatory=is_all)

    @staticmethod
    def _get_span_listener_from_config(config):
        SPAN_LISTENERS = {
            sl_class.__name__: sl_class 
            for sl_class in ThundraSpanListener.__subclasses__()
        }

        if 'listener' not in config:
            listener_class = None
        else:
            listener = config.get('listener')
            listener_type = listener.get('type')
            listener_config = listener.get('config')
            try:
                listener_class = SPAN_LISTENERS[listener_type]
            except KeyError:
                listener_class = None
                logger.error('given span listener class %s is not found', listener_type)

        listener = None
        if listener_class is not None:
            if listener_config is not None:
                listener = listener_class.from_config(listener_config)
            else:
                return listener_class()
        return listener
