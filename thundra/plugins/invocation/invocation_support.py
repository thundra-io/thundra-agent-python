class InvocationSupport:
    __instance = None

    @staticmethod
    def get_instance():
        return InvocationSupport() if InvocationSupport.__instance is None else InvocationSupport.__instance

    def __init__(self):
        InvocationSupport.__instance = self
        self.__tags = {}

    def set_tag(self, key, value):
        self.__tags[key] = value

    def set_many(self, tags):
        self.__tags.update(tags)

    def get_tag(self, key):
        if key in self.__tags:
            return self.__tags[key]
        return None
    
    def get_tags_dict(self):
        return self.__tags.copy()

    def remove_tag(self, key):
        return self.__tags.pop(key, None)
    
    def clear(self):
        self.__tags.clear()
    
    def __setitem__(self, key, value):
        self.set_tag(key, value)
    
    def __getitem__(self, key):
        return self.get_tag(key)

    def __delitem__(self, key):
        self.remove_tag(key)