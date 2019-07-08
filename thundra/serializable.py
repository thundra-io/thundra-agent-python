import abc

ABC = abc.ABCMeta('ABC', (object,), {})


class Serializable(ABC):

    @abc.abstractmethod
    def serialize(self):
        return self.__dict__
