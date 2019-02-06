import logging
from thundra.listeners import ThundraSpanListener
from thundra.listeners.thundra_span_filterer import ThundraSpanFilter
from thundra.listeners.thundra_span_filterer import ThundraSpanFilterer

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
        SPAN_LISTENERS = {
            sl_class.__name__: sl_class 
            for sl_class in ThundraSpanListener.__subclasses__()
        }

        if 'listener' not in config:
            listener_class = None
        else:
            try:
                listener_class = SPAN_LISTENERS[config['listener']]
            except KeyError:
                listener_class = None
                logger.error('given span listener class %s is not found', config['listener'])
        
        listener_config = {}
        filter_configs = {}
        kwarg_prefix = 'config.'
        filter_prefix = 'filter'
        for k, v in config.items():
            if k.startswith(kwarg_prefix):
                listener_config[k[len(kwarg_prefix):]] = v
            elif k.startswith(filter_prefix):
                first_dot_idx = k.find('.') 
                filter_id = k[:first_dot_idx]
                filter_arg = k[first_dot_idx+1:]
                if filter_configs.get(filter_id) is None:
                    filter_configs[filter_id] = {}
                filter_configs[filter_id][filter_arg] = v

        filters = [ThundraSpanFilter.from_config(c) for c in filter_configs.values()]
        
        filterer = None
        if len(filters) > 0:
            filterer = ThundraSpanFilterer(span_filters=filters)

        listener = None
        if listener_class is not None:
            listener = listener_class.from_config(listener_config)
        
        return FilteringSpanListener(listener=listener, filterer=filterer)
    
