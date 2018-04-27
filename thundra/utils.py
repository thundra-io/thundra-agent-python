import os
import sys

from thundra import constants


def get_environment_variable(key):
    return os.environ.get(key)


def should_disable(disable_by_env, disable_by_param=False):
    if disable_by_env == 'true':
        return True
    elif disable_by_env == 'false':
        return False
    else:
        return disable_by_param


def get_common_report_data_from_environment_variable():
    aws_lambda_log_stream = get_environment_variable(constants.AWS_LAMBDA_LOG_STREAM_NAME)
    log_stream = aws_lambda_log_stream.split("]")[1] if aws_lambda_log_stream is not None else ''
    aws_lambda_function_version = get_environment_variable(constants.AWS_LAMBDA_FUNCTION_VERSION)
    application_version = aws_lambda_function_version if aws_lambda_function_version is not None else ''
    thundra_application_profile = get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE)
    application_profile = thundra_application_profile if thundra_application_profile is not None else ''
    aws_region = get_environment_variable(constants.AWS_REGION)
    region = aws_region if aws_region is not None else ''
    data = {
        constants.AWS_LAMBDA_LOG_STREAM_NAME: log_stream,
        constants.AWS_LAMBDA_FUNCTION_VERSION: application_version,
        constants.THUNDRA_APPLICATION_PROFILE: application_profile,
        constants.AWS_REGION: region
    }
    return data


#### memory ####
def process_memory_usage():
    try:
        with open('/proc/self/statm', 'r') as procfile:
            process_memory_usages = procfile.readline()
            size = process_memory_usages.split(' ')[0]
            size_in_bytes = float(size)*1024
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
            # count from /proc/stat: user, nice, system, idle, iowait, irc, softirq, steal, guest
            for usage in system_cpu_usages.split(' ')[2:]:
                if count == 10:
                    break
                elif count == 0 or count == 2:
                    system_cpu_used += int(usage)
                system_cpu_total += int(usage)
                count += 1
            return float(system_cpu_total), float(system_cpu_used)
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(3)

