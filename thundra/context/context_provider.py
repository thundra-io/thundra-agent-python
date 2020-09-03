import abc

ABC = abc.ABCMeta('ABC', (object,), {})


class ContextProvider(ABC):
    @abc.abstractmethod
    def get(self):
        raise Exception("should be implemented")

    @abc.abstractmethod
    def set(self, execution_context):
        raise Exception("should be implemented")

    @abc.abstractmethod
    def clear(self):
        raise Exception("should be implemented")
