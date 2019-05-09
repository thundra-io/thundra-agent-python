from abc import ABC, abstractmethod


class BaseSampler(ABC):

    @abstractmethod
    def is_sampled(self, args):
        raise Exception("should be implemented")
