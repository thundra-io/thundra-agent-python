from __future__ import absolute_import
import logging
import os
import re
import uuid

from catchpoint import constants
from catchpoint.compat import urlparse
from opentracing.scope_managers import ThreadLocalScopeManager

logger = logging.getLogger(__name__)


def generate_id():
    return str(uuid.uuid4())


def generate_id_from(value):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, value))


def get_env_variable(key, default=None):
    return os.environ.get(key, default)


def get_aws_function_name(arn):
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


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(_Singleton('SingletonMeta', (object,), {})): pass

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


def process_trace_def_var(value):
    value = value.strip().split('[')
    path = value[0].split('.')
    trace_args = {}

    function_prefix = path[-1][:-1] if path[-1] != '*' else ''
    module_path = ".".join(path[:-1])
    trace_string = value[1].strip(']').split(',')
    for arg in trace_string:
        arg = arg.split('=')
        try:
            trace_args[arg[0]] = arg[1]
        except:
            pass

    return module_path, function_prefix, trace_args


def get_allowed_functions(module):
    allowed_functions = []
    for prop in vars(module):
        # TO DO: differentiate functions
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
    region = get_env_variable(constants.AWS_REGION, default='')
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

    normalized_timeout_margin = int((384.0 / memory) * timeout_margin)
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
    region = get_env_variable(constants.AWS_REGION)

    if region:
        return '{}.collector.catchpoint.com'.format(region)

    return "collector.catchpoint.com"


def get_compiled_operation_type_patterns():
    compiled = []
    for pattern in constants.OperationTypeMappings["patterns"]:
        compiled.append(re.compile(pattern))
    return compiled


def extract_api_gw_resource_name(event):
    try:
        resource_path = None
        if 'resource' in event:
            resource_path = event['resource']
        else:
            resource_path = event['requestContext']['http']['path']
            stage_prefix = '/' + event['requestContext']['stage']
            if resource_path.startswith(stage_prefix):
                resource_path = resource_path[len(stage_prefix):]

        return resource_path
    except:
        return None


def get_normalized_path(url_path, path_depth):
    path_seperator_count = 0
    normalized_path = ''
    prev_c = ''
    for c in url_path:
        if c == '/' and prev_c != '/':
            path_seperator_count += 1

        if path_seperator_count > path_depth:
            break

        normalized_path += c
        prev_c = c
    return normalized_path


def parse_http_url(url, url_path_depth):
    url_dict = {
        'path': '',
        'query': '',
        'host': '',
        'url': url
    }
    try:
        parsed_url = urlparse(url)
        url_dict['path'] = parsed_url.path
        url_dict['query'] = parsed_url.query
        url_dict['host'] = parsed_url.netloc

        normalized_path = get_normalized_path(parsed_url.path, url_path_depth)
        url_dict['operation_name'] = parsed_url.hostname + normalized_path

        url_dict['url'] = parsed_url.hostname + parsed_url.path
    except Exception:
        pass
    return url_dict


def arrange_scope_manager(scope_manager):
    if scope_manager is None:
        try:
            import sys
            if (sys.version_info[0] > 3) or (sys.version_info[0] == 3 and sys.version_info[1] > 7) or (sys.version_info[0] == 3 and sys.version_info[1] == 7 and sys.version_info[2] != 0):
                from opentracing.scope_managers.contextvars import ContextVarsScopeManager
                scope_manager = ContextVarsScopeManager()
            else:
                scope_manager = ThreadLocalScopeManager()
        except Exception:
            scope_manager = ThreadLocalScopeManager()
    return scope_manager


# Excluded url's
EXCLUDED_URLS = {
    str.endswith: [
        'catchpoint.com',
    ],
    str.__contains__: [
        'amazonaws.com',
        'accounts.google.com',
    ],
}

# Exclude exception urls 
EXCLUDE_EXCEPTION_URLS = {
    str.__contains__: [
        '.execute-api.',
        '.elb.'
    ]
}
