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
}

SpanTags = {
    'SPAN_TYPE': 'span.type',
    'OPERATION_TYPE': 'operation.type',
}

SpanTypes = {
    'REDIS': 'Redis',
    'RDB': 'RDB',
    'HTTP': 'HTTP',
    'AWS_DYNAMO': 'AWS-DynamoDB',
    'AWS_SQS': 'AWS-SQS',
    'AWS_SNS': 'AWS-SNS',
    'AWS_KINESIS': 'AWS-Kinesis',
    'AWS_FIREHOSE': 'AWS-Firehose',
    'AWS_S3': 'AWS-S3',
    'AWS_LAMBDA': 'AWS-Lambda',
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
}

SNSRequestTypes = {
    'Publish': 'WRITE',
}

AwsSNSTags = {
    'TOPIC_NAME': 'aws.sns.topic.name',
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
    'FUNCTION_NAME': 'aws.lambda.function.name',
    'FUNCTION_QUALIFIER': 'aws.lambda.function.qualifier',
    'INVOCATION_TYPE': 'aws.lambda.invocation.type',
    'INVOCATION_PAYLOAD': 'aws.lambda.invocation.payload',
}

LambdaRequestType = {
    'InvokeAsync': 'CALL',
    'Invoke': 'CALL',
}
