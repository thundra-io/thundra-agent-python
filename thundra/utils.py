import os
import logging
from urllib.parse import urlparse
from thundra import constants

logger = logging.getLogger(__name__)

def get_configuration(key, default=None):
    return os.environ.get(key, default=default)

def str_to_proper_type(val):
    result = val
    try:
        result = str2bool(val)
    except ValueError:
        try:
            result = int(val)
        except ValueError:
            try:
                result = float(val)
            except ValueError:
                result = val.strip('"')
    
    return result


def get_application_id(context):
    aws_lambda_log_stream_name = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
    application_id = aws_lambda_log_stream_name.split("]")[1] if aws_lambda_log_stream_name is not None else ''
    return application_id


def get_aws_lambda_function_memory_size():
    return os.environ.get(constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE)


#### memory ####
def process_memory_usage():
    try:
        with open('/proc/self/status', 'r') as procfile:
            mems = {}
            for line in procfile:
                fields = line.split(':')
                try:
                    mem_key = fields[0]
                    mem_val = (fields[1].split())[0]
                    mems[mem_key] = mem_val
                except IndexError:
                    continue
            
            size_from_env_var = get_aws_lambda_function_memory_size()
            if not size_from_env_var:
                size = int(mems['VmSize'])
                size_in_bytes = int(size * 1024)
            else:
                size_in_bytes = int(float(size_from_env_var) * 1048576)

            used_mem_in_kb = int(mems['VmRSS']) + int(mems['VmSwap'])
            used_mem_in_bytes = used_mem_in_kb * 1024

            return size_in_bytes, used_mem_in_bytes
    except Exception as e:
        logger.error('ERROR: {}'.format(e))
        return 0, 0

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
    except Exception as e:
        logger.error('ERROR: {}'.format(e))
        return 0


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
    except Exception as e:
        logger.error('ERROR: {}'.format(e))
        return 0, 0


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


def str2bool(val):
    if val is not None:
        if val.lower() in ("yes", "true", "t", "1"):
            return True
        elif val.lower() in ("no", "false", "f", "0"):
            return False
    raise ValueError


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

def is_excluded_url(url):
    host = urlparse(url).netloc

    for method in EXCLUDE_EXCEPTION_URLS:
        for exclude_exception_url in EXCLUDE_EXCEPTION_URLS[method]:
            if method(host, exclude_exception_url):
                return False

    for method in EXCLUDED_URLS:
        for excluded_url in EXCLUDED_URLS[method]:
            if method(host, excluded_url):
                return True
    return False
    

# Excluded url's 
EXCLUDED_URLS = {
    str.endswith: [
        'thundra.io',
    ],
    str.__contains__: [
        'amazonaws.com',
        'accounts.google.com',
    ],
}

# Exclude exception urls 
EXCLUDE_EXCEPTION_URLS = {
    str.__contains__: [
        'execute-api',
    ]
}