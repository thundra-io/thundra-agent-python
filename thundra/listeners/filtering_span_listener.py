from thundra.listeners.thundra_span_listener import ThundraSpanListener

class FilteringSpanListener(ThundraSpanListener):
    
    def __init__(self, listener=None, span_filterer=None):
        self.listener = listener
        self.span_filterer = span_filterer

    def on_span_started(self, span):
        if self.listener is None:
            return

        if self.span_filterer is None or self.span_filterer.accept(span):
            self.listener.on_span_started(span)
    
    def on_span_finished(self, span):
        if self.listener is None:
            return
        
        if self.span_filterer is None or self.span_filterer.accept(span):
            self.listener.on_span_finished(span)
