import abc

class Serializable(abc.ABC):

    @abc.abstractmethod
    def serialize(self):
        return self.__dict__
