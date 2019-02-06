import abc

class ThundraSpanListener(abc.ABC):
    @abc.abstractmethod
    def on_span_started(self, operation_name):
        raise Exception("should be implemented")

    @abc.abstractmethod
    def on_span_finished(self, span):
        raise Exception("should be implemented")
    
    @staticmethod
    @abc.abstractmethod
    def from_config(config):
        raise Exception("should be implemented")

    @staticmethod
    @abc.abstractmethod
    def should_raise_exceptions():
        raise Exception("should be implemented")