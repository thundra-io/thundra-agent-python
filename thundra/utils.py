import os
import logging
import re

from thundra.compat import urlparse
from thundra.plugins.invocation import invocation_support
from thundra import constants

logger = logging.getLogger(__name__)

def get_configuration(key, default=None):
    return os.environ.get(key, default)

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

def get_application_instance_id(context):
    aws_lambda_log_stream_name = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, '')
    try:
        return aws_lambda_log_stream_name.split(']')[1]
    except:
        return ''

def get_application_id(context):
    arn = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, '')

    region = get_aws_region_from_arn(arn)
    account_no = 'sam_local' if sam_local_debugging() else get_aws_account_no(arn)
    function_name = get_aws_funtion_name(arn)

    application_id_template = 'aws:lambda:{region}:{account_no}:{function_name}'
    
    return application_id_template.format(region=region, account_no=account_no, function_name=function_name)

def get_aws_funtion_name(arn):
    return get_arn_part(arn, 6)

def get_aws_region_from_arn(arn):
    return get_arn_part(arn, 3)

def get_aws_account_no(arn):
    return get_arn_part(arn, 4)

def get_arn_part(arn, index):
    # ARN format: arn:aws:lambda:{region}:{account_no}:function:{function_name}
    try:
        return arn.split(":")[index]
    except:
        return ""

def get_aws_lambda_function_memory_size():
    return os.environ.get(constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE)

def sam_local_debugging():
    return os.environ.get(constants.AWS_SAM_LOCAL) == 'true'

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

def get_default_timeout_margin():
    region = get_configuration(constants.AWS_REGION, default='')
    size_from_env_var = get_aws_lambda_function_memory_size()
    memory = -1
    if size_from_env_var:
        memory = int(float(size_from_env_var))

    timeout_margin = 1000

    if region == 'us-west-2':
        timeout_margin = 200
    elif region.startswith('us-west-'):
        timeout_margin = 400
    elif region.startswith('us-') or region.startswith('ca-'):
        timeout_margin = 600
    elif region.startswith('sa-'):
        timeout_margin = 800

    normalized_timeout_margin = int((384.0/memory) * timeout_margin)
    return max(timeout_margin, normalized_timeout_margin)

def parse_x_ray_trace_info():
    xray_trace_header = os.environ.get("_X_AMZN_TRACE_ID")
    xray_info = {"trace_id": None, "segment_id": None}
    if xray_trace_header:
        for trace_header_part in xray_trace_header.split(";"):
            trace_info = trace_header_part.split("=")
            if len(trace_info) == 2 and trace_info[0] == "Root":
                xray_info["trace_id"] = trace_info[1]
            elif len(trace_info) == 2 and trace_info[0] == "Parent":
                xray_info["segment_id"] = trace_info[1]

    return xray_info

def get_nearest_collector():
    region = get_configuration(constants.AWS_REGION, default="us-west-2")

    if region.startswith("us-west-"):
        return "api.thundra.io"
    elif region == "eu-west-1":
        return "api-eu-west-1.thundra.io"
    elif region.startswith("us-east-") or region.startswith("sa-") or region.startswith("ca-"):
        return "api-us-east-1.thundra.io"
    elif region.startswith("eu-"):
        return "api-eu-west-2.thundra.io"
    elif region.startswith("ap-"):
        return "api-ap-northeast-1.thundra.io"

    return "api.thundra.io"

def get_compiled_operation_type_patterns():
    compiled = []
    for pattern in constants.OperationTypeMappings["patterns"]:
        compiled.append(re.compile(pattern))
    return compiled

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