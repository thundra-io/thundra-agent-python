from threading import Lock
from thundra.listeners.thundra_span_listener import ThundraSpanListener

default_error_message = "Error injected by Thundra!"
default_error_type = Exception

class ErrorInjectorSpanListener(ThundraSpanListener):
    def __init__(self, 
        error_message=default_error_message, 
        error_type=default_error_type,
        inject_on_finish=False,
        inject_count_freq=1
    ):
        self._counter = 0
        self._lock = Lock()

        self.error_message = error_message
        self.error_type = error_type
        self.inject_on_finish = inject_on_finish
        self.inject_count_freq = max(inject_count_freq, 1)
    
    def on_span_started(self, span):
        if (not self.inject_on_finish
            and self.able_to_raise()):
            self.raise_error()

    def on_span_finished(self, span):
        if (self.inject_on_finish
            and self.able_to_raise()):
            self.raise_error()

    def raise_error(self):
        err = self.error_type(self.error_message)
        raise err
    
    def able_to_raise(self):
        if self.increment_and_get_counter() % self.inject_count_freq == 0:
            return True
        return False

    def increment_and_get_counter(self):
        with self._lock:
            self._counter += 1
        
        return self._counter
    
    @staticmethod
    def from_config(config):
        return ErrorInjectorSpanListener()