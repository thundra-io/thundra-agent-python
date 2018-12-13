import os
import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

import thundra.utils as utils
from thundra import constants
from thundra.plugins.trace.traceable import Traceable


class ImportPatcher(utils.Singleton):

    def __init__(self):
        self.modules_map = self.__process_env_var_modules_to_instrument()

        for module_path in self.modules_map.keys():
            sys.meta_path.insert(0, YetAnotherFinder(module_path))
            # sys.meta_path.insert(0, AnotherFinder(module_path))
            # sys.meta_path.insert(0, ThundraFinder(module_path))

    @staticmethod
    def __process_env_var_modules_to_instrument():
        modules = {}
        for env_variable, value in utils.get_all_env_variables().items():
            if env_variable.startswith(constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG):
                value.strip()
                for val in value.split('|'):
                    try:
                        module_path, function_prefix, arguments = utils.process_trace_def_env_var(val)
                    except:
                        module_path = None
                    if module_path != None:
                        modules[module_path] = [function_prefix, arguments]

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
            spec = super().find_spec(fullname, path, target)
            loader = ThundraLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)

class YetAnotherFinder(PathFinder):
    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            path = "/var/task"
            if "." in fullname:
                path = path + "/" + fullname.split(".")[0]
                filePath = path + "/" + fullname.split(".")[1] + ".py"
            else:
                filePath = path + "/" + fullname

            if os.path.exists(filePath):
                if (filePath not in sys.path):
                    loader = ThundraLoader(fullname, filePath)
                    mod = ModuleSpec(fullname, loader)
                    return mod
            else:
                return None


class AnotherFinder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if (fullname == self.module_name):
            if path is None or path == "":
                path = [os.getcwd()]  # top level import --

            if "." in fullname:
                *parents, name = fullname.split(".")
            else:
                name = fullname

            for entry in path:
                if os.path.isdir(os.path.join(entry, name)):
                    # this module has child modules
                    filename = os.path.join(entry, name, "__init__.py")
                    submodule_locations = [os.path.join(entry, name)]

                else:
                    filename = os.path.join(entry, name + ".py")
                    submodule_locations = None

                if not os.path.exists(filename):
                    continue
                else:
                    spec = super().find_spec(fullname, path, target)
                    loader = ThundraLoader(fullname, spec.origin)
                    moduleSpec = ModuleSpec(fullname, loader)
                    if moduleSpec is not None:
                        return moduleSpec
                    else:
                        return None
        return None  # we don't know how to import this


# Loading the module in a load time
class ThundraLoader(SourceFileLoader):
    def __init__(self, fullname, path):
        super().__init__(fullname, path)

    def exec_module(self, module):
        super().exec_module(module)
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
                if (function_prefix == "*") or (function_prefix in function['functionName']):
                    funcName = function['functionName']
                    if function['type'] == "class":
                        mod = __import__(module.__name__, fromlist=[funcName])
                        klass = getattr(mod, function['className'])
                        setattr(klass, funcName,
                                Traceable(trace_args=trace_args,
                                          trace_return_value=trace_return_value,
                                          trace_error=trace_error)(getattr(klass, funcName)))
                    else:
                        setattr(module, funcName,
                                Traceable(trace_args=trace_args,
                                          trace_return_value=trace_return_value,
                                          trace_error=trace_error)(getattr(module, funcName)))

        else:
            for function in allowed_functions:
                funcName = function['functionName']
                setattr(module, funcName,
                        Traceable(trace_args=trace_args,
                                  trace_return_value=trace_return_value,
                                  trace_error=trace_error)(getattr(module, funcName)))

        return module
