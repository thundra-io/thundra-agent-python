import os

from thundra import constants


def get_thundra_apikey():
    return os.environ['thundra_apiKey'] if 'thundra_apiKey' in os.environ else None


def is_thundra_disabled():
    should_thundra_disabled = os.environ['thundra_disable'] if 'thundra_disable' in os.environ else 'false'
    return should_disable(should_thundra_disabled)


def should_disable(disable_by_env, disable_by_param=False):
    if disable_by_env == 'true':
        return True
    elif disable_by_env == 'false':
        return False
    else:
        return disable_by_param

def is_thundra_trace_disabled():
    return os.environ['thundra_trace_disable'] if 'thundra_trace_disable' in os.environ else ''


def is_thundra_lambda_publish_cloudwatch_enabled():
    return os.environ['thundra_lambda_publish_cloudwatch_enable'] if 'thundra_lambda_publish_cloudwatch_enable' in os.environ else 'false'


def is_thundra_lambda_audit_request_skipped():
    return os.environ['thundra_lambda_audit_request_skip'] if 'thundra_lambda_audit_request_skip' in os.environ else ''


def is_thundra_lambda_audit_response_skipped():
    return os.environ['thundra_lambda_audit_response_skip'] if 'thundra_lambda_audit_response_skip' in os.environ else ''


def get_thundra_application_profile():
    return os.environ['thundra_applicationProfile'] if 'thundra_applicationProfile' in os.environ else ''


def get_aws_lambda_log_stream():
    return os.environ['AWS_LAMBDA_LOG_STREAM_NAME'] if 'AWS_LAMBDA_LOG_STREAM_NAME' in os.environ else None


def get_aws_lambda_function_version():
    return os.environ['AWS_LAMBDA_FUNCTION_VERSION'] if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ else ""


def get_aws_region():
    return os.environ['AWS_REGION'] if 'AWS_REGION' in os.environ else ""
