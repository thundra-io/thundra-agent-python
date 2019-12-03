from thundra.config import utils

import os

def initialize_properties():
    property_accessor = utils.get_property_accessor()
    initialize_properties_from_environment_variables(property_accessor)
    print(property_accessor.get_properties())


def initialize_properties_from_environment_variables(property_accessor):
    env_variables = os.environ

    for var_name in env_variables:
        val = env_variables.get(var_name).strip()
        if var_name.startswith("x_thundra_"):
            var_name = var_name[2:]

        if var_name.startswith("thundra_agent_lambda"):
            var_name = var_name.replace("thundra_agent_lambda", "thundra_agent", 1)

        if var_name.startswith("thundra_"):
            property_accessor.put_property(var_name, val)

    