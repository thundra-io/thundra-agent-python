import abc

ABC = abc.ABCMeta('ABC', (object,), {})


class ApplicationInfoProvider(ABC):

    @abc.abstractmethod
    def get_application_info(self):
        pass