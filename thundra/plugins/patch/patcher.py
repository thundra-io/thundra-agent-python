from thundra import constants
import thundra.utils as utils
from thundra.plugins.trace.traceable import Traceable
import six
import inspect

import sys
import os
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader


class ImportPatcher(utils.Singleton):

    def __init__(self):
        self.modules_map = self.process_env_var_modules_to_instrument()

        for module_path in self.modules_map.keys():
            sys.meta_path.insert(0, ThundraFinder(module_path))

    def process_env_var_modules_to_instrument(self):
        modules = {}
        for env_variable, value in utils.get_all_env_variables().items():
            if env_variable.startswith(constants.THUDRA_TRACE_DEF):
                try:
                    module_path, function_prefix, arguments = utils.process_trace_def_env_var(value)
                except:
                    module_path = None
                if module_path != None:
                    modules[module_path] = [function_prefix, arguments]
        return modules
    
    def get_module_function_prefix(self, module_name):
        if self.modules_map[module_name]:
            return self.modules_map[module_name][0]
        return None
    
    def get_trace_arguments(self, module_name):
        if self.modules_map[module_name]:
            return self.modules_map[module_name][1]
        return None
    
class ThundraFinder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            loader = ThundraLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)



#Loading the module in a load time
class ThundraLoader(SourceFileLoader):
  
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
            trace_error= utils.str2bool(trace_args_list[constants.TRACE_ERROR])
        except:
            trace_error = False

        allowed_functions = utils.get_allowed_functions(module)

        if function_prefix != '':
            for function in allowed_functions:
                if function_prefix in function:
                    setattr(module, function, Traceable(trace_args=trace_args, trace_return_value=trace_return_value, trace_error=trace_error)(getattr(module, function)))
        else:
            for function in allowed_functions:
                setattr(module, function, Traceable(trace_args=trace_args, trace_return_value=trace_return_value, trace_error=trace_error)(getattr(module, function)))
        
        return module


