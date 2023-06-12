from threading import Lock


class WrapperFactory:
    lock = Lock()
    wrappers = {}

    @staticmethod
    def get_or_create(wrapper_class):
        with WrapperFactory.lock:
            if wrapper_class in WrapperFactory.wrappers:
                return WrapperFactory.wrappers[wrapper_class]
            else:
                WrapperFactory.wrappers[wrapper_class] = wrapper_class()
                return WrapperFactory.wrappers[wrapper_class]
