import logging
from thundra import utils

logger = logging.getLogger(__name__)


class PropertyAccessor():

    def get_property(self, property_name):
        raise Exception("should be implemented")

    def get_properties(self):
        raise Exception("should be implemented")

    def put_property(self, property_name, property_value):
        raise Exception("should be implemented")

    def put_properties(self, properties):
        raise Exception("should be implemented")

    def remove_property(self, property_name, property_value):
        raise Exception("should be implemented")
    
    def get_bool_property(self, property_name, default):
        prop = self.get_property(property_name)
        try:
            bool_prop = utils.str2bool(prop)
            return bool_prop
        except ValueError:
            return default
    
    def get_str_property(self, property_name, default):
        prop = self.get_property(property_name)
        if prop:
            return prop
        return default

    def get_int_property(self, property_name, default):
        prop = self.get_property(property_name)
        try:
            int_prop = int(prop)
        except (ValueError, TypeError):
            int_prop = default
        return int_prop
    