from thundra import utils, constants

def api_key(api_key_from_params):
    api_key_from_env_var = utils.get_configuration(constants.THUNDRA_APIKEY)
    if api_key_from_env_var is not None:
        return api_key_from_env_var
    return api_key_from_params

def trace_disabled(disable_trace):
    try:
        disable_trace_by_env = utils.str2bool(utils.get_configuration(constants.THUNDRA_DISABLE_TRACE))
        return disable_trace_by_env
    except ValueError:
        return disable_trace
    
def metric_disabled(disable_metric):
    try:
        disable_metric_by_env = utils.str2bool(utils.get_configuration(constants.THUNDRA_DISABLE_METRIC))
        return disable_metric_by_env
    except ValueError:
        return disable_metric

def log_disabled(disable_log):
    try:
        disable_log_by_env = utils.str2bool(utils.get_configuration(constants.THUNDRA_DISABLE_LOG))
        return disable_log_by_env
    except ValueError:
        return disable_log

def trace_instrument_disabled():
    try:
        disable_trace_instrument_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_DISABLE))
        return disable_trace_instrument_by_env
    except ValueError:
        return False

def disable_stdout_logs():
    try:
        disable_stdout_logs_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_LOG_CONSOLE_PRINT_DISABLE))
        return disable_stdout_logs_by_env
    except ValueError:
        return False

def timeout_margin():
    try:
        timeout_margin = int(utils.get_configuration(constants.THUNDRA_LAMBDA_TIMEOUT_MARGIN))
    except (ValueError, TypeError):
        timeout_margin = 0
    if timeout_margin > 0:
        return timeout_margin
    return constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN

def thundra_disabled():
    try:
        thundra_disabled_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_DISABLE))
        return thundra_disabled_by_env
    except ValueError:
        return False

def debug_enabled():
    try:
        debug_enabled_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_DEBUG_ENABLE))
        return debug_enabled_by_env
    except ValueError:
        return False

def report_cw_enabled():
    try:
        cw_enabled_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE))
        return cw_enabled_by_env
    except ValueError:
        return False

def report_base_url():
    return utils.get_configuration(constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL)

def skip_trace_request():
    try:
        skip_req_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP))
        return skip_req_by_env
    except ValueError:
        return False

def skip_trace_response():
    try:
        skip_resp_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP))
        return skip_resp_by_env
    except ValueError:
        return False

def xray_trace_enabled():
    try:
        enable_xray_trace_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY))
        return enable_xray_trace_by_env
    except ValueError:
        return False

def http_integration_disabled():
    try:
        disable_http_integration_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_DISABLE_HTTP_INTEGRATION))
        return disable_http_integration_by_env
    except ValueError:
        return False

def redis_integration_disabled():
    try:
        disable_redis_integration_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_DISABLE_REDIS_INTEGRATION))
        return disable_redis_integration_by_env
    except ValueError:
        return False

def rdb_integration_disabled():
    try:
        disable_rdb_integration_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_DISABLE_RDB_INTEGRATION))
        return disable_rdb_integration_by_env
    except ValueError:
        return False

def aws_integration_disabled():
    try:
        disable_aws_integration_by_env = utils.str2bool(
            utils.get_configuration(constants.THUNDRA_DISABLE_AWS_INTEGRATION))
        return disable_aws_integration_by_env
    except ValueError:
        return False
