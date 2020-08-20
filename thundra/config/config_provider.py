import os

from thundra.config.config_metadata import CONFIG_METADATA


class ConfigProvider:
    configs = {}

    @staticmethod
    def __init__(options=None):
        ConfigProvider.clear()
        if options is not None:
            config_options = options.get('config', {})
            for opt in config_options:
                ConfigProvider.traverse_config_object(config_options.get(opt), opt)
        ConfigProvider.initialize_config_from_environment_variables()
        ConfigProvider.add_non_lambda_aliases()

    @staticmethod
    def initialize_config_from_environment_variables():
        env_variables = os.environ

        for var_name in env_variables:
            if var_name.upper().startswith("THUNDRA_"):
                env_var_name = ConfigProvider.env_var_to_config_name(var_name)
                val = env_variables.get(var_name).strip()
                env_var_type = ConfigProvider.get_config_type(env_var_name)
                ConfigProvider.configs[env_var_name] = ConfigProvider.parse(val, env_var_type)

    @staticmethod
    def traverse_config_object(obj, path):
        if not isinstance(obj, dict):
            if not path.startswith('thundra.agent.'):
                path = 'thundra.agent.' + path
            path = path.lower()
            prop_type = ConfigProvider.get_config_type(path)
            ConfigProvider.configs[path] = ConfigProvider.parse(obj, prop_type)
        else:
            for prop_name in obj:
                prop_val = obj.get(prop_name)
                prop_path = path + '.' + prop_name
                ConfigProvider.traverse_config_object(prop_val, prop_path)

    @staticmethod
    def add_non_lambda_aliases():
        alias_configs = {}
        for config_name in ConfigProvider.configs:
            if config_name.startswith('thundra.agent.lambda'):
                value = ConfigProvider.configs[config_name]
                alias_configs[config_name.replace('thundra.agent.lambda', 'thundra.agent', 1)] = value
        ConfigProvider.configs.update(alias_configs)

    @staticmethod
    def get(key, default_value=None):
        value = ConfigProvider.configs.get(key)
        if value is not None:
            return value
        if default_value is not None:
            return default_value
        if CONFIG_METADATA.get(key):
            return CONFIG_METADATA[key].get('defaultValue')
        return None

    @staticmethod
    def get_config_type(config_name):
        config_metadata = CONFIG_METADATA.get(config_name)
        if config_metadata:
            return config_metadata.get('type')
        else:
            if config_name.startswith('thundra.agent.lambda.'):
                config_name = config_name.replace('thundra.agent.lambda.', 'thundra.agent.', 1)
                config_metadata = CONFIG_METADATA.get(config_name)
                if config_metadata:
                    return config_metadata.get('type')
        return None

    @staticmethod
    def parse(value, var_type):
        if var_type == 'string':
            return value
        if var_type == 'int':
            return ConfigProvider.convert_to_int(value)
        if var_type == 'boolean':
            return ConfigProvider.convert_to_bool(value)
        return ConfigProvider.str_to_proper_type(value)

    @staticmethod
    def str2bool(val):
        if type(val) == bool:
            return val
        if isinstance(val, str):
            if val.lower() in ("yes", "true", "t", "1"):
                return True
            elif val.lower() in ("no", "false", "f", "0"):
                return False
        raise ValueError

    @staticmethod
    def str_to_proper_type(val):
        try:
            result = ConfigProvider.str2bool(val)
        except ValueError:
            try:
                result = int(val)
            except ValueError:
                try:
                    result = float(val)
                except ValueError:
                    result = val.strip('"')

        return result

    @staticmethod
    def convert_to_bool(value, default=False):
        if type(value) == bool:
            return value
        try:
            return ConfigProvider.str2bool(value)
        except ValueError:
            return default

    @staticmethod
    def convert_to_int(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def config_name_to_env_var(config_name):
        return config_name.upper().replace('.', '_')

    @staticmethod
    def env_var_to_config_name(env_var_name):
        return env_var_name.lower().replace('_', '.')

    @staticmethod
    def clear():
        ConfigProvider.configs.clear()

    @staticmethod
    def set(key, value):
        ConfigProvider.configs[key] = ConfigProvider.parse(value, ConfigProvider.get_config_type(key))


ConfigProvider.__init__()
