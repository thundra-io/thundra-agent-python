from thundra.config.standard_property_accessor import StandardPropertyAccessor


property_accessor = StandardPropertyAccessor()

def get_property_accessor():
    return property_accessor

def get_string_property(property_name, default=None):
    return property_accessor.get_property(property_name, default)

def get_bool_property(property_name, default=False):
    return property_accessor.get_bool_property(property_name, default)

def get_int_property(property_name, default=0):
    return property_accessor.get_int_property(property_name, default)
