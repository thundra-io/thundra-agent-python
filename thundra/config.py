from thundra import utils, constants

def bool_from_env(key, default=False):
    try:
        from_env = utils.str2bool(
            utils.get_configuration(key))
        return from_env
    except ValueError:
        return default

def int_from_env(key, default=0):
    try:
        from_env = int(utils.get_configuration(key))
    except (ValueError, TypeError):
        from_env = default
    return from_env

def str_from_env(key, default=None):
    return utils.get_configuration(key, default=default)


def api_key(api_key_from_params):
    return str_from_env(constants.THUNDRA_APIKEY, default=api_key_from_params)

def trace_disabled(disable_trace):
    return bool_from_env(constants.THUNDRA_DISABLE_TRACE, default=disable_trace)
    
def metric_disabled(disable_metric):
    return bool_from_env(constants.THUNDRA_DISABLE_METRIC, default=disable_metric)

def log_disabled(disable_log):
    return bool_from_env(constants.THUNDRA_DISABLE_LOG, default=disable_log)

def trace_instrument_disabled():
    return bool_from_env(constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_DISABLE)

def disable_stdout_logs():
    return bool_from_env(constants.THUNDRA_LAMBDA_LOG_CONSOLE_PRINT_DISABLE)

def timeout_margin():
    timeout_margin = int_from_env(constants.THUNDRA_LAMBDA_TIMEOUT_MARGIN)
    if timeout_margin > 0:
        return timeout_margin
    return constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN

def thundra_disabled():
    return bool_from_env(constants.THUNDRA_DISABLE)

def debug_enabled():
    return bool_from_env(constants.THUNDRA_LAMBDA_DEBUG_ENABLE)

def report_cw_enabled():
    return bool_from_env(constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE)

def report_base_url():
    return str_from_env(constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL)

def skip_trace_request():
    return bool_from_env(constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP)

def skip_trace_response():
    return bool_from_env(constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP)

def xray_trace_enabled():
    return bool_from_env(constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY)

def http_integration_disabled():
    return bool_from_env(constants.THUNDRA_DISABLE_HTTP_INTEGRATION)

def redis_integration_disabled():
    return bool_from_env(constants.THUNDRA_DISABLE_REDIS_INTEGRATION)

def rdb_integration_disabled():
    return bool_from_env(constants.THUNDRA_DISABLE_RDB_INTEGRATION)

def aws_integration_disabled():
    return bool_from_env(constants.THUNDRA_DISABLE_AWS_INTEGRATION)

def count_aware_metric_freq():
    return int_from_env(constants.THUNDRA_AGENT_METRIC_COUNT_AWARE_SAMPLER_COUNT_FREQ, default=-1)

def time_aware_metric_freq():
    return int_from_env(constants.THUNDRA_AGENT_METRIC_TIME_AWARE_SAMPLER_TIME_FREQ, default=-1)
