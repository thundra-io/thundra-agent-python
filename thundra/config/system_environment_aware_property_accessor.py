import os

from thundra.config.property_accessor import PropertyAccessor
from thundra import utils


class SystemEnvironmentAwarePropertyAccessor(PropertyAccessor):

    def __init__(self):
        pass

    def get_property(self, property_name):
        return os.environ.get(property_name)
    
    def get_properties(self):
        return os.environ
    
    
    
    