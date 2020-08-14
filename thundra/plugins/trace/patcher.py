from __future__ import absolute_import, unicode_literals

import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

import thundra.utils as utils
from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.plugins.trace.traceable import Traceable


class ImportPatcher(utils.Singleton):

    def __init__(self):
        self.modules_map = self.__process_env_var_modules_to_instrument()

        for module_path in self.modules_map.keys():
            sys.meta_path.insert(0, ThundraFinder(module_path))

    @staticmethod
    def __process_env_var_modules_to_instrument():
        modules = {}
        for variable in ConfigProvider.configs:
            value = ConfigProvider.get(variable)
            if variable.startswith(config_names.THUNDRA_TRACE_INSTRUMENT_TRACEABLECONFIG):
                try:
                    module_path, function_prefix, arguments = utils.process_trace_def_var(value)
                    if module_path is not None:
                        modules[module_path] = [function_prefix, arguments]
                except:
                    pass

        return modules

    def get_module_function_prefix(self, module_name):
        try:
            return self.modules_map[module_name][0]
        except:
            return None

    def get_trace_arguments(self, module_name):
        try:
            return self.modules_map[module_name][1]
        except:
            return None


class ThundraFinder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super(ThundraFinder, self).find_spec(fullname, path, target)
            loader = ThundraLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)


# Loading the module in a load time
class ThundraLoader(SourceFileLoader):

    def exec_module(self, module):
        super(ThundraLoader, self).exec_module(module)
        import_patcher = ImportPatcher()
        module_name = utils.get_module_name(module)
        function_prefix = import_patcher.get_module_function_prefix(module_name)
        trace_args_list = import_patcher.get_trace_arguments(module_name)
        try:
            trace_args = utils.str2bool(trace_args_list[constants.TRACE_ARGS])
        except:
            trace_args = False

        try:
            trace_return_value = utils.str2bool(trace_args_list[constants.TRACE_RETURN_VALUE])
        except:
            trace_return_value = False

        try:
            trace_error = utils.str2bool(trace_args_list[constants.TRACE_ERROR])
        except:
            trace_error = True

        allowed_functions = utils.get_allowed_functions(module)

        if function_prefix != '':
            for function in allowed_functions:
                if function_prefix in function:
                    setattr(module, function,
                            Traceable(trace_args=trace_args,
                                      trace_return_value=trace_return_value,
                                      trace_error=trace_error)(getattr(module, function)))
        else:
            for function in allowed_functions:
                setattr(module, function,
                        Traceable(trace_args=trace_args,
                                  trace_return_value=trace_return_value,
                                  trace_error=trace_error)(getattr(module, function)))

        return module
