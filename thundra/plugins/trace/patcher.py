import os
import sys
import re
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

import thundra.utils as utils
from thundra import constants
from thundra.plugins.trace.traceable import Traceable


class ImportPatcher(utils.Singleton):

    def __init__(self):
        try:
            self.modules_map = self.__process_env_var_modules_to_instrument()
            for module_path_regex in self.modules_map.keys():
                finder = ThundraFinder(module_path_regex, self.modules_map[module_path_regex][0],
                                       self.modules_map[module_path_regex][1])
                sys.meta_path.insert(0, finder)

        except Exception as e:
            print(e)

    @staticmethod
    def __process_env_var_modules_to_instrument():
        modules = {}
        for env_variable, value in utils.get_all_env_variables().items():
            if env_variable.startswith(constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG):
                value = value.strip()
                for val in value.split('|'):
                    try:
                        module_path_regex, function_regex, arguments = utils.process_trace_def_env_var(val)
                    except:
                        module_path_regex = None
                    if module_path_regex:
                        modules[module_path_regex] = [function_regex, arguments]

        return modules


class ThundraFinder(PathFinder):

    def __init__(self, module_path_regex, function_regex, trace_arguments):
        self.module_path_regex = module_path_regex
        self.function_regex = function_regex
        self.trace_arguments = trace_arguments

    def find_spec(self, fullname, path=None, target=None):
        try:
            if (re.match(self.module_path_regex, fullname)):
                spec = super().find_spec(fullname, path, target)
                if not spec:
                    return None
                loader = ThundraLoader(fullname, spec.origin, self.function_regex, self.trace_arguments)
                _spec = ModuleSpec(fullname, loader)
                _spec.submodule_search_locations = spec.submodule_search_locations
                return _spec
        except Exception as e:
            print(e)
            return None


# Loading the module in a load time
class ThundraLoader(SourceFileLoader):
    def __init__(self, fullname, path, function_regex, trace_args):
        super().__init__(fullname, path)
        self.function_regex = function_regex
        self.trace_args = trace_args

    def exec_module(self, module):
        try:
            super().exec_module(module)
        except Exception as e:
            print(e)
            return module

        try:
            trace_args, trace_return_value, trace_error = self.get_trace_parameters()
            allowed_functions = utils.get_allowed_functions(module)

            if self.function_regex:
                for function in allowed_functions:
                    if re.match(self.function_regex, function['functionName']):
                        func_name = function['functionName']
                        if function['type'] == "class":
                            mod = __import__(module.__name__, fromlist=[func_name])
                            klass = getattr(mod, function['className'])
                            func = getattr(klass, func_name)
                            # If wrapped before, skip
                            if not hasattr(func, "thundra_wrapper"):
                                setattr(klass, func_name,
                                        Traceable(trace_args=trace_args,
                                                  trace_return_value=trace_return_value,
                                                  trace_error=trace_error)(func))
                        else:
                            func = getattr(module, func_name)
                            # If wrapped before, skip
                            if not hasattr(func, "thundra_wrapper"):
                                setattr(module, func_name,
                                        Traceable(trace_args=trace_args,
                                                  trace_return_value=trace_return_value,
                                                  trace_error=trace_error)(func))
        except Exception as e:
            print(e)

        return module

    def get_trace_parameters(self):
        try:
            trace_args = utils.str2bool(self.trace_args[constants.TRACE_ARGS])
        except:
            trace_args = False

        try:
            trace_return_value = utils.str2bool(self.trace_args[constants.TRACE_RETURN_VALUE])
        except:
            trace_return_value = False

        try:
            trace_error = utils.str2bool(self.trace_args[constants.TRACE_ERROR])
        except:
            trace_error = True

        return trace_args, trace_return_value, trace_error
