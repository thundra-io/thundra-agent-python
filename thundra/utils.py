import os
import sys
import copy
import types

from thundra import constants

from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader
from thundra.plugins.trace.traceable import Traceable



def get_environment_variable(key, default=None):
    return os.environ.get(key, default=default)


def should_disable(disable_by_env, disable_by_param=False):
    if disable_by_env == 'true':
        return True
    elif disable_by_env == 'false':
        return False
    return disable_by_param


def get_application_id(context):
    aws_lambda_log_stream_name = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
    applicationId = aws_lambda_log_stream_name.split("]")[1] if aws_lambda_log_stream_name is not None else ''
    return applicationId

def get_aws_lambda_function_memory_size():
    return os.environ.get(constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE)

#### memory ####
def process_memory_usage():
    try:
        with open('/proc/self/statm', 'r') as procfile:
            process_memory_usages = procfile.readline()
            size_from_env_var = get_aws_lambda_function_memory_size()
            if not size_from_env_var:
                size = process_memory_usages.split(' ')[0]
                size_in_bytes = float(size) * 1024
            else:
                size_in_bytes = float(size_from_env_var) * 1000000

            resident = process_memory_usages.split(' ')[1]
            resident_in_bytes = float(resident)*1024
            return size_in_bytes, resident_in_bytes
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)

def system_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as procfile:
            total = procfile.readline()
            total_memory = total.split(': ')[1].split('kB')[0]
            total_mem_in_bytes = int(total_memory)*1024
            free = procfile.readline()
            free_memory = free.split(': ')[1].split('kB')[0]
            free_mem_in_bytes = int(free_memory)*1024
            return total_mem_in_bytes, free_mem_in_bytes
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)


##### cpu #####
def process_cpu_usage():
    try:
        with open('/proc/self/stat', 'r') as procfile:
            process_cpu_usages = procfile.readline()
            # get utime from /proc/<pid>/stat, 14 item
            u_time = process_cpu_usages.split(' ')[13]
            # get stime from proc/<pid>/stat, 15 item
            s_time = process_cpu_usages.split(' ')[14]
            # count total process used time
            process_cpu_used = int(u_time) + int(s_time)
            return (float(process_cpu_used))
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)


def system_cpu_usage():
    try:
        with open('/proc/stat', 'r') as procfile:
            system_cpu_usages = procfile.readline()
            system_cpu_used = 0
            system_cpu_total = 0
            count = 0
            for usage in system_cpu_usages.split(' ')[2:]:
                if count == 5:
                    break
                elif count != 3 and count != 4:
                    system_cpu_used += int(usage)
                system_cpu_total += int(usage)
                count += 1
            return float(system_cpu_total), float(system_cpu_used)
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(3)

#####################################################################
###
#####################################################################


class Singleton(object):
    _instances = {}
    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]

def get_all_env_variables():
    return os.environ

def get_module_name(module):
    return module.__name__

def string_to_list(target, indicator):
    return target.split(indicator)

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def process_trace_def_env_var(value):
    value = value.strip().split('[')
    path = value[0].split('.')
    trace_args = {}

    function_prefix = path[-1][:-1] if path[-1] != '*' else ''
    module_path = ".".join(path[:-1])
    trace_string = value[1].strip(']').split(',')
    for arg  in trace_string:
        arg = arg.split('=')
        try:
            trace_args[arg[0]] = arg[1]
        except:
            pass

    return module_path, function_prefix, trace_args

def get_allowed_functions(module):
    allowed_functions = []
    for prop in vars(module):
        #TO DO: differentiate functions
        allowed_functions.append(str(prop))
    return allowed_functions

def get_aws_region_from_arn(func_arn):
    return func_arn.split(':')[3] if len(func_arn.split(':')) >= 3 else ""
