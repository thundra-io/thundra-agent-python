DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f %z"

HOST = "https://api.thundra.io"
PATH = "/v1/monitoring-data"

REQUEST_COUNT = 0

THUNDRA_APIKEY = 'thundra_apiKey'
THUNDRA_DISABLE = 'thundra_agent_lambda_disable'
THUNDRA_APPLICATION_DOMAIN_NAME = 'thundra_agent_lambda_application_domainName'
THUNDRA_APPLICATION_CLASS_NAME = 'thundra_agent_lambda_application_className'
THUNDRA_APPLICATION_STAGE = 'thundra_agent_lambda_application_stage'
THUNDRA_APPLICATION_VERSION = 'thundra_agent_lambda_application_version'
THUNDRA_AGENT_VERSION = '2.0.0'

THUNDRA_LAMBDA_TIMEOUT_MARGIN = 'thundra_agent_lambda_timeout_margin'
THUNDRA_LAMBDA_REPORT_REST_BASEURL = 'thundra_agent_lambda_report_rest_baseUrl'
THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE = 'thundra_agent_lambda_report_cloudwatch_enable'
THUNDRA_DISABLE_TRACE = 'thundra_agent_lambda_trace_disable'
THUNDRA_DISABLE_METRIC = 'thundra_agent_lambda_metric_disable'
THUNDRA_DISABLE_LOG = 'thundra_agent_lambda_log_disable'

THUNDRA_LAMBDA_TRACE_REQUEST_SKIP = 'thundra_agent_lambda_trace_request_skip'
THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP = 'thundra_agent_lambda_trace_response_skip'
THUNDRA_LAMBDA_TRACE_INSTRUMENT_DISABLE = 'thundra_agent_lambda_trace_instrument_disable'
THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG = 'thundra_agent_lambda_trace_instrument_traceableConfig'

AWS_LAMBDA_APPLICATION_ID = 'AWS_LAMBDA_APPLICATION_ID'
AWS_LAMBDA_LOG_STREAM_NAME = 'AWS_LAMBDA_LOG_STREAM_NAME'
AWS_LAMBDA_FUNCTION_VERSION = 'AWS_LAMBDA_FUNCTION_VERSION'
AWS_REGION = 'AWS_REGION'
AWS_LAMBDA_FUNCTION_MEMORY_SIZE = "AWS_LAMBDA_FUNCTION_MEMORY_SIZE"
AWS_LAMBDA_APPLICATION_DOMAIN_NAME = 'API'
AWS_LAMBDA_APPLICATION_CLASS_NAME = 'AWS-Lambda'

CONTEXT_FUNCTION_NAME = 'function_name'
CONTEXT_FUNCTION_VERSION = 'function_version'
CONTEXT_FUNCTION_PLATFORM = 'AWS-Lambda'
CONTEXT_MEMORY_LIMIT_IN_MB = 'memory_limit_in_mb'
CONTEXT_INVOKED_FUNCTION_ARN = 'invoked_function_arn'
CONTEXT_AWS_REQUEST_ID = 'aws_request_id'
CONTEXT_LOG_GROUP_NAME = 'log_group_name'
CONTEXT_LOG_STREAM_NAME = 'log_stream_name'

TRACE_ARGS = 'trace_args'
TRACE_RETURN_VALUE = 'trace_return_value'
TRACE_ERROR = 'trace_error'

LIST_SEPARATOR = ','

DEFAULT_LAMBDA_TIMEOUT_MARGIN = 200
DATA_FORMAT_VERSION = '2.0'
