DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f %z"

HOST = "https://api.thundra.io/v1"
PATH = "/monitoring-data"
COMPOSITE_DATA_PATH = "/composite-monitoring-data"

REQUEST_COUNT = 0

THUNDRA_APIKEY = 'thundra_apiKey'
THUNDRA_DISABLE = 'thundra_agent_lambda_disable'
THUNDRA_APPLICATION_DOMAIN_NAME = 'thundra_agent_lambda_application_domainName'
THUNDRA_APPLICATION_CLASS_NAME = 'thundra_agent_lambda_application_className'
THUNDRA_APPLICATION_STAGE = 'thundra_agent_lambda_application_stage'
THUNDRA_APPLICATION_VERSION = 'thundra_agent_lambda_application_version'
THUNDRA_AGENT_VERSION = '2.3.0'

LAMBDA_APPLICATION_DOMAIN_NAME = 'API'
LAMBDA_APPLICATION_CLASS_NAME = 'AWS-Lambda'
LAMBDA_FUNCTION_PLATFORM = 'AWS Lambda'
THUNDRA_LAMBDA_TIMEOUT_MARGIN = 'thundra_agent_lambda_timeout_margin'
THUNDRA_LAMBDA_REPORT_REST_BASEURL = 'thundra_agent_lambda_report_rest_baseUrl'
THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_ENABLED = 'thundra_agent_lambda_report_rest_composite_enable'
THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE = 'thundra_agent_lambda_report_cloudwatch_enable'
THUNDRA_LAMBDA_REPORT_CLOUDWATCH_COMPOSITE_ENABLED = 'thundra_agent_lambda_report_cloudwatch_composite_enable'

THUNDRA_DISABLE_TRACE = 'thundra_agent_lambda_trace_disable'
THUNDRA_DISABLE_METRIC = 'thundra_agent_lambda_metric_disable'
THUNDRA_DISABLE_LOG = 'thundra_agent_lambda_log_disable'

THUNDRA_LAMBDA_TRACE_REQUEST_SKIP = 'thundra_agent_lambda_trace_request_skip'
THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP = 'thundra_agent_lambda_trace_response_skip'
THUNDRA_LAMBDA_TRACE_INSTRUMENT_DISABLE = 'thundra_agent_lambda_trace_instrument_disable'
THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG = 'thundra_agent_lambda_trace_instrument_traceableConfig'
THUNDRA_LAMBDA_TRACE_ENABLE_XRAY = 'thundra_agent_lambda_trace_enable_xray'

TRIGGER_OPERATION_NAME_TAG = 'x-thundra-trigger-operation-name'
TRIGGER_CLASS_NAME_TAG = 'x-thundra-trigger-class-name'
TRIGGER_DOMAIN_NAME_TAG = 'x-thundra-trigger-domain-name'

THUNDRA_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE = 'thundra_agent_lambda_trace_kinesis_request_enable'
THUNDRA_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE = 'thundra_agent_lambda_trace_firehose_request_enable'
THUNDRA_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE = 'thundra_agent_lambda_trace_cloudwatchlog_request_enable'

THUNDRA_AGENT_METRIC_TIME_AWARE_SAMPLER_TIME_FREQ = 'thundra_agent_lambda_metric_sample_sampler_timeAware_timeFreq'
THUNDRA_AGENT_METRIC_COUNT_AWARE_SAMPLER_COUNT_FREQ = 'thundra_agent_lambda_metric_sample_sampler_countAware_countFreq'
DEFAULT_METRIC_SAMPLING_TIME_FREQ = 5 * 60 * 1000
DEFAULT_METRIC_SAMPLING_COUNT_FREQ = 100

THUNDRA_DISABLE_HTTP_INTEGRATION = 'thundra_agent_lambda_trace_integrations_http_disable'
THUNDRA_DISABLE_RDB_INTEGRATION = 'thundra_agent_lambda_trace_integrations_rdb_disable'
THUNDRA_DISABLE_AWS_INTEGRATION = 'thundra_agent_lambda_trace_integrations_aws_disable'
THUNDRA_DISABLE_REDIS_INTEGRATION = 'thundra_agent_lambda_trace_integrations_redis_disable'
THUNDRA_DISABLE_ES_INTEGRATION = 'thundra_agent_lambda_trace_integrations_elasticsearch_disable'

THUNDRA_MASK_REDIS_COMMAND = 'thundra_agent_lambda_trace_integrations_redis_command_mask'
THUNDRA_MASK_RDB_STATEMENT = 'thundra_agent_lambda_trace_integrations_rdb_statement_mask'
THUNDRA_MASK_DYNAMODB_STATEMENT = 'thundra_agent_lambda_trace_integrations_aws_dynamodb_statement_mask'
THUNDRA_MASK_ES_BODY = 'thundra_agent_lambda_trace_integrations_elasticsearch_body_mask'
THUNDRA_MASK_SNS_MESSAGE = 'thundra_agent_lambda_trace_integrations_aws_sns_message_mask'
THUNDRA_MASK_SQS_MESSAGE = 'thundra_agent_lambda_trace_integrations_aws_sqs_message_mask'
THUNDRA_MASK_LAMBDA_PAYLOAD = 'thundra_agent_lambda_trace_integrations_aws_lambda_payload_mask'
THUNDRA_MASK_HTTP_BODY = 'thundra_agent_lambda_trace_integrations_aws_http_body_mask'

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

APPLICATION_ID_PROP_NAME = 'thundra_agent_lambda_application_id'
APPLICATION_DOMAIN_NAME_PROP_NAME = 'thundra_agent_lambda_application_domainName'
APPLICATION_CLASS_NAME_PROP_NAME = 'thundra_agent_lambda_application_className'
APPLICATION_NAME_PROP_NAME = 'thundra_agent_lambda_application_name'
APPLICATION_VERSION_PROP_NAME = 'thundra_agent_lambda_application_version'
APPLICATION_STAGE_PROP_NAME = 'thundra_agent_lambda_application_stage'
APPLICATION_TAG_PROP_NAME_PREFIX = 'thundra_agent_lambda_application_tag_'

TRACE_ARGS = 'trace_args'
TRACE_RETURN_VALUE = 'trace_return_value'
TRACE_ERROR = 'trace_error'

LIST_SEPARATOR = ','

DEFAULT_LAMBDA_TIMEOUT_MARGIN = 200
DATA_FORMAT_VERSION = '2.0'

THUNDRA_LAMBDA_DEBUG_ENABLE = 'thundra_agent_lambda_debug_enable'
THUNDRA_LAMBDA_LOG_CONSOLE_PRINT_DISABLE = 'thundra_agent_lambda_log_console_disable'
THUNDRA_LAMBDA_SPAN_LISTENER = 'thundra_agent_lambda_trace_span_listener'
THUNDRA_LAMBDA_SPAN_LISTENER_INFO_TAG = 'thundra.span_listener.info'

DEFAULT_REPORT_REST_COMPOSITE_BATCH_SIZE = 100
DEFAULT_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE = 10

THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_BATCH_SIZE = 'thundra_agent_lambda_report_rest_composite_batchsize'
THUNDRA_LAMBDA_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE = 'thundra_agent_lambda_report_cloudwatch_composite_batchsize'

ENABLE_DYNAMODB_TRACE_INJECTION = 'thundra_agent_trace_integrations_dynamodb_trace_injection_enable'
DISABLE_LAMBDA_TRACE_INJECTION = 'thundra_agent_trace_integrations_aws_lambda_traceInjection_disable'

#### INTEGRATIONS ####

AWS_SERVICE_REQUEST = 'AWSServiceRequest'

DomainNames = {
    'AWS': 'AWS',
    'DB': 'DB',
    'MESSAGING': 'Messaging',
    'STREAM': 'Stream',
    'STORAGE': 'Storage',
    'API': 'API',
    'CACHE': 'Cache',
    'SCHEDULE': 'Schedule',
    'LOG': 'Log',
    'CDN': 'CDN',
}

ClassNames = {
    'AWSSERVICE': 'AWSService',
    'DYNAMODB': 'AWS-DynamoDB',
    'SQS': 'AWS-SQS',
    'SNS': 'AWS-SNS',
    'KINESIS': 'AWS-Kinesis',
    'FIREHOSE': 'AWS-Firehose',
    'S3': 'AWS-S3',
    'LAMBDA': 'AWS-Lambda',
    'RDB': 'RDB',
    'REDIS': 'Redis',
    'HTTP': 'HTTP',
    'MYSQL': 'MYSQL',
    'POSTGRESQL': 'POSTGRESQL',
    'ELASTICSEARCH': 'ELASTICSEARCH',
    'SCHEDULE': 'AWS-CloudWatch-Schedule',
    'CLOUDWATCHLOG': 'AWS-CloudWatch-Log',
    'CLOUDFRONT': 'AWS-CloudFront',
    'APIGATEWAY': 'AWS-APIGateway',
}

DBTags = {
    'DB_STATEMENT': 'db.statement',
    'DB_STATEMENT_TYPE': 'db.statement.type',
    'DB_INSTANCE': 'db.instance',
    'DB_TYPE': 'db.type',
    'DB_HOST': 'db.host',
    'DB_PORT': 'db.port',
    'DB_USER': 'db.user',
}

AwsDynamoTags = {
    'TABLE_NAME': 'aws.dynamodb.table.name',
    'REQUEST_THROTTLED': 'aws.dynamodb.request.throttled',
}

DBTypes = {
    'DYNAMODB': 'aws-dynamodb',
    'REDIS': 'redis',
    'ELASTICSEARCH': 'elasticsearch',
}

SpanTags = {
    'OPERATION_TYPE': 'operation.type',
    'DB_INSTANCE': 'db.instance',
    'DB_TYPE': 'db.type',
    'DB_HOST': 'db.host',
    'TRIGGER_DOMAIN_NAME': 'trigger.domainName',
    'TRIGGER_CLASS_NAME': 'trigger.className',
    'TRIGGER_OPERATION_NAMES': 'trigger.operationNames',
    'TOPOLOGY_VERTEX': 'topology.vertex',
    'DB_STATEMENT': 'db.statement',
    'DB_STATEMENT_TYPE': 'db.statement.type:',
    'TRACE_LINKS': 'trace.links'
}

DynamoDBRequestTypes = {
    'BatchGetItem': 'READ',
    'BatchWriteItem': 'WRITE',
    'CreateTable': 'WRITE',
    'CreateGlobalTable': 'WRITE',
    'DeleteItem': 'DELETE',
    'DeleteTable': 'DELETE',
    'GetItem': 'READ',
    'PutItem': 'WRITE',
    'Query': 'READ',
    'Scan': 'READ',
    'UpdateItem': 'WRITE',

}

AwsSDKTags = {
    'SERVICE_NAME': 'aws.service.name',
    'REQUEST_NAME': 'aws.request.name',
    'HOST': 'host',
}

SQSRequestTypes = {
    'ReceiveMessage': 'READ',
    'SendMessage': 'WRITE',
    'SendMessageBatch': 'WRITE',
    'DeleteMessage': 'DELETE',
    'DeleteMessageBatch': 'DELETE',
}

AwsSQSTags = {
    'QUEUE_NAME': 'aws.sqs.queue.name',
    'MESSAGE': 'aws.sqs.message',
    'MESSAGES': 'aws.sqs.messages',
}

SNSRequestTypes = {
    'Publish': 'WRITE',
}

AwsSNSTags = {
    'TOPIC_NAME': 'aws.sns.topic.name',
    'MESSAGE': 'aws.sns.message',
}

AwsKinesisTags = {
    'STREAM_NAME': 'aws.kinesis.stream.name',
}

KinesisRequestTypes = {
    'GetRecords': 'READ',
    'PutRecords': 'WRITE',
    'PutRecord': 'WRITE',
}

AwsFirehoseTags = {
    'STREAM_NAME': 'aws.firehose.stream.name',
}

FirehoseRequestTypes = {
    'PutRecordBatch': 'WRITE',
    'PutRecord': 'WRITE',
}

S3RequestTypes = {
    'DeleteBucket': 'DELETE',
    'CreateBucket': 'WRITE',
    'copyObject': 'WRITE',
    'DeleteObject': 'DELETE',
    'deleteObjects': 'DELETE',
    'GetObject': 'READ',
    'GetObjectAcl': 'READ',
    'ListBucket': 'READ',
    'PutObject': 'WRITE',
    'PutObjectAcl': 'WRITE',
}

AwsS3Tags = {
    'BUCKET_NAME': 'aws.s3.bucket.name',
    'OBJECT_NAME': 'aws.s3.object.name',
}

AwsLambdaTags = {
    'FUNCTION_NAME': 'aws.lambda.name',
    'FUNCTION_QUALIFIER': 'aws.lambda.qualifier',
    'INVOCATION_TYPE': 'aws.lambda.invocation.type',
    'INVOCATION_PAYLOAD': 'aws.lambda.invocation.payload',
}

LambdaRequestType = {
    'InvokeAsync': 'CALL',
    'Invoke': 'CALL',
}

HttpTags = {
    'HTTP_METHOD': 'http.method',
    'HTTP_URL': 'http.url',
    'HTTP_PATH': 'http.path',
    'HTTP_HOST': 'http.host',
    'HTTP_STATUS': 'http.status_code',
    'QUERY_PARAMS': 'http.query_params',
    'BODY': 'http.body',
}

RedisCommandTypes = {
    'APPEND': 'WRITE',
    'BGREWRITEAOF': 'WRITE',
    'BGSAVE': 'WRITE',
    'BITCOUNT': 'READ',
    'BITFIELD': 'WRITE',
    'BITOP': 'WRITE',
    'BITPOS': 'READ',
    'BLPOP': 'DELETE',
    'BRPOP': 'DELETE',
    'BRPOPLPUSH': 'WRITE',
    'BZPOPMIN': 'DELETE',
    'BZPOPMAX': 'DELETE',
    'DBSIZE': 'READ',
    'DECR': 'WRITE',
    'DECRBY': 'WRITE',
    'DELETE': 'DELETE',
    'EVAL': 'EXECUTE',
    'EVALSHA': 'EXECUTE',
    'EXISTS': 'READ',
    'EXPIRE': 'WRITE',
    'EXPIREAT': 'WRITE',
    'FLUSHALL': 'DELETE',
    'FLUSHDB': 'DELETE',
    'GEOADD': 'WRITE',
    'GEOHASH': 'READ',
    'GEOPOS': 'READ',
    'GEODIST': 'READ',
    'GEORADIUS': 'READ',
    'GEORADIUSBYMEMBER': 'READ',
    'GET': 'READ',
    'GETBIT': 'READ',
    'GETRANGE': 'READ',
    'GETSET': 'WRITE',
    'HDEL': 'DELETE',
    'HEXISTS': 'READ',
    'HGET': 'READ',
    'HGETALL': 'READ',
    'HINCRBY': 'WRITE',
    'HINCRBYFLOAT': 'WRITE',
    'HKEYS': 'READ',
    'HLEN': 'READ',
    'HMGET': 'READ',
    'HMSET': 'WRITE',
    'HSET': 'WRITE',
    'HSETNX': 'WRITE',
    'HSTRLEN': 'READ',
    'HVALS': 'READ',
    'INCR': 'WRITE',
    'INCRBY': 'WRITE',
    'INCRBYFLOAT': 'WRITE',
    'KEYS': 'READ',
    'LINDEX': 'READ',
    'LINSERT': 'WRITE',
    'LLEN': 'READ',
    'LPOP': 'DELETE',
    'LPUSH': 'WRITE',
    'LPUSHX': 'WRITE',
    'LRANGE': 'READ',
    'LREM': 'DELETE',
    'LSET': 'WRITE',
    'LTRIM': 'DELETE',
    'MGET': 'READ',
    'MSET': 'WRITE',
    'MSETNX': 'WRITE',
    'PERSIST': 'WRITE',
    'PEXPIRE': 'WRITE',
    'PEXPIREAT': 'WRITE',
    'PFADD': 'WRITE',
    'PFCOUNT': 'READ',
    'PFMERGE': 'WRITE',
    'PSETEX': 'WRITE',
    'PUBLISH': 'WRITE',
    'RPOP': 'DELETE',
    'RPOPLPUSH': 'WRITE',
    'RPUSH': 'WRITE',
    'RPUSHX': 'WRITE',
    'SADD': 'WRITE',
    'SCARD': 'READ',
    'SDIFFSTORE': 'WRITE',
    'SET': 'WRITE',
    'SETBIT': 'WRITE',
    'SETEX': 'WRITE',
    'SETNX': 'WRITE',
    'SETRANGE': 'WRITE',
    'SINTER': 'READ',
    'SINTERSTORE': 'WRITE',
    'SISMEMBER': 'READ',
    'SMEMBERS': 'READ',
    'SMOVE': 'WRITE',
    'SORT': 'WRITE',
    'SPOP': 'DELETE',
    'SRANDMEMBER': 'READ',
    'SREM': 'DELETE',
    'STRLEN': 'READ',
    'SUNION': 'READ',
    'SUNIONSTORE': 'WRITE',
    'ZADD': 'WRITE',
    'ZCARD': 'READ',
    'ZCOUNT': 'READ',
    'ZINCRBY': 'WRITE',
    'ZINTERSTORE': 'WRITE',
    'ZLEXCOUNT': 'READ',
    'ZPOPMAX': 'DELETE',
    'ZPOPMIN': 'DELETE',
    'ZRANGE': 'READ',
    'ZRANGEBYLEX': 'READ',
    'ZREVRANGEBYLEX': 'READ',
    'ZRANGEBYSCORE': 'READ',
    'ZRANK': 'READ',
    'ZREM': 'DELETE',
    'ZREMRANGEBYLEX': 'DELETE',
    'ZREMRANGEBYRANK': 'DELETE',
    'ZREMRANGEBYSCORE': 'DELETE',
    'ZREVRANGE': 'READ',
    'ZREVRANGEBYSCORE': 'READ',
    'ZREVRANK': 'READ',
    'ZSCORE': 'READ',
    'ZUNIONSTORE': 'WRITE',
    'SCAN': 'READ',
    'SSCAN': 'READ',
    'HSCAN': 'READ',
    'ZSCAN': 'READ',
    'XADD': 'WRITE',
    'XRANGE': 'READ',
    'XREVRANGE': 'READ',
    'XLEN': 'READ',
    'XREAD': 'READ',
    'XREADGROUP': 'READ',
    'XPENDING': 'READ',
}

RedisTags = {
    'REDIS_HOST': 'redis.host',
    'REDIS_PORT': 'redis.port',
    'REDIS_COMMAND': 'redis.command',
    'REDIS_COMMANDS': 'redis.commands',
    'REDIS_COMMAND_TYPE': 'redis.command.type',
    'REDIS_COMMAND_ARGS': 'redis.command.args',
}

ESTags = {
    'ES_URI': 'elasticsearch.uri',
    'ES_METHOD': 'elasticsearch.method',
    'ES_PARAMS': 'elasticsearch.params',
    'ES_BODY': 'elasticsearch.body',
    'ES_HOSTS': 'elasticsearch.hosts',
}

AwsXrayConstants = {
    'DEFAULT_OPERATION_NAME': 'AWS X-Ray',
    'XRAY_SUBSEGMENTED_TAG_NAME': 'THUNDRA::XRAY_SUBSEGMENTED',
}
