from abc import ABCMeta, abstractmethod

ABC = ABCMeta('ABC', (object,), {})

class BaseSampler(ABC):

    @abstractmethod
    def is_sampled(self, args):
        raise Exception("should be implemented")
