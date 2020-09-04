from collections import OrderedDict
from thundra._version import __version__

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f %z"

HOST = "https://api.thundra.io/v1"
PATH = "/monitoring-data"
COMPOSITE_DATA_PATH = "/composite-monitoring-data"

THUNDRA_AGENT_VERSION = __version__

LAMBDA_APPLICATION_DOMAIN_NAME = 'API'
LAMBDA_APPLICATION_CLASS_NAME = 'AWS-Lambda'
LAMBDA_APPLICATION_PLATFORM = 'AWS Lambda'

TRIGGER_OPERATION_NAME_TAG = 'x-thundra-trigger-operation-name'
TRIGGER_CLASS_NAME_TAG = 'x-thundra-trigger-class-name'
TRIGGER_DOMAIN_NAME_TAG = 'x-thundra-trigger-domain-name'
TRIGGER_RESOURCE_NAME_TAG = 'x-thundra-resource-name'

DEFAULT_METRIC_SAMPLING_TIME_FREQ = 5 * 60 * 1000
DEFAULT_METRIC_SAMPLING_COUNT_FREQ = 100

AWS_LAMBDA_APPLICATION_ID = 'AWS_LAMBDA_APPLICATION_ID'
AWS_SAM_LOCAL = 'AWS_SAM_LOCAL'
AWS_LAMBDA_LOG_STREAM_NAME = 'AWS_LAMBDA_LOG_STREAM_NAME'
AWS_LAMBDA_FUNCTION_VERSION = 'AWS_LAMBDA_FUNCTION_VERSION'
AWS_LAMBDA_FUNCTION_NAME = 'AWS_LAMBDA_FUNCTION_NAME'
AWS_REGION = 'AWS_REGION'
AWS_LAMBDA_FUNCTION_MEMORY_SIZE = "AWS_LAMBDA_FUNCTION_MEMORY_SIZE"
AWS_LAMBDA_APPLICATION_DOMAIN_NAME = 'API'
AWS_LAMBDA_APPLICATION_CLASS_NAME = 'AWS-Lambda'

CONTEXT_FUNCTION_NAME = 'function_name'
CONTEXT_FUNCTION_VERSION = 'function_version'
CONTEXT_APPLICATION_PLATFORM = 'AWS-Lambda'
CONTEXT_MEMORY_LIMIT_IN_MB = 'memory_limit_in_mb'
CONTEXT_INVOKED_FUNCTION_ARN = 'invoked_function_arn'
CONTEXT_AWS_REQUEST_ID = 'aws_request_id'
CONTEXT_LOG_GROUP_NAME = 'log_group_name'
CONTEXT_LOG_STREAM_NAME = 'log_stream_name'

TRACE_ARGS = 'trace_args'
TRACE_RETURN_VALUE = 'trace_return_value'
TRACE_ERROR = 'trace_error'

MAX_INCOMING_TRACE_LINKS = 10
MAX_OUTGOING_TRACE_LINKS = 20

LIST_SEPARATOR = ','

DEFAULT_LAMBDA_TIMEOUT_MARGIN = 200
DATA_FORMAT_VERSION = '2.0'

THUNDRA_LAMBDA_SPAN_LISTENER_INFO_TAG = 'thundra.span_listener.info'

DEFAULT_REPORT_REST_COMPOSITE_BATCH_SIZE = 100
DEFAULT_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE = 10

#### INTEGRATIONS ####

DEFAULT_MONGO_COMMAND_SIZE_LIMIT = 128 * 1024
DEFAULT_REPORT_TIMEOUT = 3

AWS_SERVICE_REQUEST = 'AWSServiceRequest'

LineByLineTracingTags = {
    'lines': 'method.lines',
    'next_span_ids': 'nextSpanIds',
    'source': 'method.source',
    'start_line': 'method.startLine',
    'args': 'method.args'
}

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
    'MONGODB': 'MONGODB',
    'SQLALCHEMY': 'SQLALCHEMY',
    'SQLITE': 'SQLITE',
    'ATHENA': 'AWS-Athena',
    'STEPFUNCTIONS': 'AWS-StepFunctions',
    'EVENTBRIDGE': 'AWS-EventBridge',
    'SES': 'AWS-SES'
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
    'DB_STATEMENT_TYPE': 'db.statement.type',
    'TRACE_LINKS': 'trace.links',
    'RESOURCE_NAMES': 'resource.names',
    'RESOURCE_TRACE_LINKS': 'resource.trace.links'
}

SecurityTags = {
    'BLOCKED': 'security.blocked',
    'VIOLATED': 'security.violated'
}

AthenaTags = {
    'S3_OUTPUT_LOCATION': "aws.athena.s3.outputLocation",
    'REQUEST_QUERY_EXECUTION_IDS': "aws.athena.request.query.executionIds",
    'RESPONSE_QUERY_EXECUTION_IDS': "aws.athena.response.query.executionIds",
    'REQUEST_NAMED_QUERY_IDS': "aws.athena.request.namedQuery.ids",
    'RESPONSE_NAMED_QUERY_IDS': "aws.athena.response.namedQuery.ids",
}

AwsSDKTags = {
    'SERVICE_NAME': 'aws.service.name',
    'REQUEST_NAME': 'aws.request.name',
    'HOST': 'host',
}

AwsStepFunctionsTags = {
    'STATE_MACHINE_ARN': 'aws.sf.state_machine.arn',
    'EXECUTION_NAME': 'aws.sf.execution.name',
    'EXECUTION_INPUT': 'aws.sf.execution.input',
    'EXECUTION_ARN': 'aws.sf.execution.arn',
    'EXECUTION_START_DATE': 'aws.sf.execution.start_date'
}

AwsSQSTags = {
    'QUEUE_NAME': 'aws.sqs.queue.name',
    'MESSAGE': 'aws.sqs.message',
    'MESSAGES': 'aws.sqs.messages',
}

AwsSNSTags = {
    'TOPIC_NAME': 'aws.sns.topic.name',
    'MESSAGE': 'aws.sns.message',
}

AwsKinesisTags = {
    'STREAM_NAME': 'aws.kinesis.stream.name',
}

AwsFirehoseTags = {
    'STREAM_NAME': 'aws.firehose.stream.name',
}

AwsS3Tags = {
    'BUCKET_NAME': 'aws.s3.bucket.name',
    'OBJECT_NAME': 'aws.s3.object.name',
}

AwsSESTags = {
    'SERVICE_REQUEST': 'AWSSESRequest',
    'SUBJECT': 'aws.ses.mail.subject',
    'BODY': 'aws.ses.mail.body',
    'TEMPLATE_NAME': 'aws.ses.mail.template.name',
    'TEMPLATE_ARN': 'aws.ses.mail.template.arn',
    'TEMPLATE_DATA': 'aws.ses.mail.template.data',
    'SOURCE': 'aws.ses.mail.source',
    'DESTINATION': 'aws.ses.mail.destination',
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
    'ES_NORMALIZED_URI': 'elasticsearch.normalized_uri'
}

AwsXrayConstants = {
    'DEFAULT_OPERATION_NAME': 'AWS X-Ray',
    'XRAY_SUBSEGMENTED_TAG_NAME': 'THUNDRA::XRAY_SUBSEGMENTED',
}

MongoDBTags = {
    'MONGODB_COMMAND': 'mongodb.command',
    'MONGODB_COMMAND_NAME': 'mongodb.command.name',
    'MONGODB_COLLECTION': 'mongodb.collection.name',
}

MongoDBCommandTypes = {
    # Aggregate Commands
    'AGGREGATE': 'READ',
    'COUNT': 'READ',
    'DISTINCT': 'READ',
    'GROUP': 'READ',
    'MAPREDUCE': 'READ',

    # Geospatial Commands
    'GEONEAR': 'READ',
    'GEOSEARCH': 'READ',

    # Query and Write Operation Commands
    'DELETE': 'DELETE',
    'EVAL': 'EXECUTE',
    'FIND': 'READ',
    'FINDANDMODIFY': 'WRITE',
    'GETLASTERROR': 'READ',
    'GETMORE': 'READ',
    'GETPREVERROR': 'READ',
    'INSERT': 'WRITE',
    'PARALLELCOLLECTIONSCAN': 'READ',
    'RESETERROR': 'WRITE',
    'UPDATE': 'WRITE',

    # Query Plan Cache Commands
    'PLANCACHECLEAR': 'DELETE',
    'PLANCACHECLEARFILTERS': 'DELETE',
    'PLANCACHELISTFILTERS': 'READ',
    'PLANCACHELISTPLANS': 'READ',
    'PLANCACHELISTQUERYSHAPES': 'READ',
    'PLANCACHESETFILTER': 'WRITE',

    # Authentication Commands
    'AUTHENTICATE': 'EXECUTE',
    'LOGOUT': 'EXECUTE',

    # User Management Commands
    'CREATEUSER': 'WRITE',
    'DROPALLUSERSFROMDATABASE': 'DELETE',
    'DROPUSER': 'DELETE',
    'GRANROLESTOUSER': 'WRITE',
    'REVOKEROLESFROMUSER': 'WRITE',
    'UPDATEUSER': 'WRITE',
    'USERSINFO': 'READ',

    # Role Management Commands
    'CREATEROLE': 'WRITE',
    'DROPROLE': 'DELETE',
    'DROPALLROLESFROMDATABASE': 'DELETE',
    'GRANTPRIVILEGESTOROLE': 'WRITE',
    'GRANTROLESTOROLE': 'WRITE',
    'INVALIDATEUSERCACHE': 'DELETE',
    'REVOKEPRIVILEGESFROMROLE': 'WRITE',
    'REVOKEROLESFROMROLE': 'WRITE',
    'ROLESINFO': 'READ',
    'UPDATEROLE': 'WRITE',

    # Replication Commands
    'ISMASTER': 'READ',
    'REPLSETABORTPRIMARYCATCHUP': 'EXECUTE',
    'REPLSETFREEZE': 'EXECUTE',
    'REPLSETGETCONFIG': 'READ',
    'REPLSETGETSTATUS': 'READ',
    'REPLSETINITIATE': 'EXECUTE',
    'REPLSETMAINTENANCE': 'EXECUTE',
    'REPLSETRECONFIG': 'EXECUTE',
    'REPLSETRESIZEOPLOG': 'EXECUTE',
    'REPLSETSTEPDOWN': 'EXECUTE',
    'REPLSETSYNCFROM': 'EXECUTE',

    # Sharding Commands
    'ADDSHARD': 'EXECUTE',
    'ADDSHARDTOZONE': 'EXECUTE',
    'BALANCERSTART': 'EXECUTE',
    'BALANCERSTATUS': 'READ',
    'BALANCERSTOP': 'EXECUTE',
    'CLEANUPORPHANED': 'EXECUTE',
    'ENABLESHARDING': 'EXECUTE',
    'FLUSHROUTERCONFIG': 'EXECUTE',
    'ISDBGRID': 'READ',
    'LISTSHARDS': 'READ',
    'MOVEPRIMARY': 'EXECUTE',
    'MERGECHUNKS': 'EXECUTE',
    'REMOVESHARD': 'EXECUTE',
    'REMOVESHARDFROMZONE': 'EXECUTE',
    'SHARDCOLLECTION': 'EXECUTE',
    'SHARDINGSTATE': 'READ',
    'SPLIT': 'EXECUTE',
    'UPDATEZONEKEYRANGE': 'EXECUTE',

    # Session Commands
    'ABORTTRANSACTION': 'EXECUTE',
    'COMMITTRANSACTION': 'EXECUTE',
    'ENDSESSIONS': 'EXECUTE',
    'KILLALLSESSIONS': 'EXECUTE',
    'KILLALLSESSIONSBYPATTERN': 'EXECUTE',
    'KILLSESSIONS': 'EXECUTE',
    'REFRESHSESSIONS': 'EXECUTE',
    'STARTSESSION': 'EXECUTE',

    # Administration Commands 
    'CLONE': 'EXECUTE',
    'CLONECOLLECTION': 'EXECUTE',
    'CLONECOLLECTIONASCAPPED': 'EXECUTE',
    'COLLMOD': 'WRITE',
    'COMPACT': 'EXECUTE',
    'CONVERTTOCAPPED': 'EXECUTE',
    'COPYDB': 'EXECUTE',
    'CREATE': 'WRITE',
    'CREATEINDEXES': 'WRITE',
    'CURRENTOP': 'READ',
    'DROP': 'DELETE',
    'DROPDATABASE': 'DELETE',
    'DROPINDEXES': 'DELETE',
    'FILEMD5': 'READ',
    'FSYNC': 'EXECUTE',
    'FSYNCUNLOCK': 'EXECUTE',
    'GETPARAMETER': 'READ',
    'KILLCURSORS': 'EXECUTE',
    'KILLOP': 'EXECUTE',
    'LISTCOLLECTIONS': 'READ',
    'LISTDATABASES': 'READ',
    'LISTINDEXES': 'READ',
    'LOGROTATE': 'EXECUTE',
    'REINDEX': 'WRITE',
    'RENAMECOLLECTION': 'WRITE',
    'REPAIRDATABASE': 'EXECUTE',
    'SETFEATURECOMPATIBILITYVERSION': 'WRITE',
    'SETPARAMETER': 'WRITE',
    'SHUTDOWN': 'EXECUTE',
    'TOUCH': 'EXECUTE',

    # Diagnostic Commands
    'BUILDINFO': 'READ',
    'COLLSTATS': 'READ',
    'CONNPOOLSTATS': 'READ',
    'CONNECTIONSTATUS': 'READ',
    'CURSORINFO': 'READ',
    'DBHASH': 'READ',
    'DBSTATS': 'READ',
    'DIAGLOGGING': 'READ',
    'EXPLAIN': 'READ',
    'FEATURES': 'READ',
    'GETCMDLINEOPTS': 'READ',
    'GETLOG': 'READ',
    'HOSTINFO': 'READ',
    'LISTCOMMANDS': 'READ',
    'PROFILE': 'READ',
    'SERVERSTATUS': 'READ',
    'SHARDCONNPOOLSTATS': 'READ',
    'TOP': 'READ',

    # Free Monitoring Commands
    'SETFREEMONITORING': 'EXECUTE',

    # Auditing Commands
    'LOGAPPLICATIONMESSAGE': 'EXECUTE',
}

OperationTypeMappings = {
    'exclusions': {
        'AWS-Lambda': {
            'ListTags': 'READ',
            'TagResource': 'WRITE',
            'UntagResource': 'WRITE',
            'EnableReplication': 'PERMISSION'
        },
        'AWS-S3': {
            'HeadBucket': 'LIST',
            'ListBucketByTags': 'READ',
            'ListBucketMultipartUploads': 'READ',
            'ListBucketVersions': 'READ',
            'ListJobs': 'READ',
            'ListMultipartUploadParts': 'READ',
            'GetBucketTagging': 'READ',
            'GetObjectVersionTagging': 'READ',
            'GetObjectTagging': 'READ',
            'GetBucketObjectLockConfiguration': 'WRITE',
            'GetObjectLegalHold': 'WRITE',
            'GetObjectRetention': 'WRITE',
            'DeleteObjectTagging': 'TAGGING',
            'DeleteObjectVersionTagging': 'TAGGING',
            'PutBucketTagging': 'TAGGING',
            'PutObjectTagging': 'TAGGING',
            'PutObjectVersionTagging': 'TAGGING',
            'AbortMultipartUpload': 'WRITE',
            'ReplicateDelete': 'WRITE',
            'ReplicateObject': 'WRITE',
            'RestoreObject': 'WRITE',
            'DeleteBucketPolicy': 'PERMISSION',
            'ObjectOwnerOverrideToBucketOwner': 'PERMISSION',
            'PutAccountPublicAccessBlock': 'PERMISSION',
            'PutBucketAcl': 'PERMISSION',
            'PutBucketPolicy': 'PERMISSION',
            'PutBucketPublicAccessBlock': 'PERMISSION',
            'PutObjectAcl': 'PERMISSION',
            'PutObjectVersionAcl': 'PERMISSION'
        },
        'AWS-SNS': {
            'ListPhoneNumbersOptedOut': 'READ',
            'ListTagsForResource': 'READ',
            'CheckIfPhoneNumberIsOptedOut': 'READ',
            'UntagResource': 'TAGGING',
            'ConfirmSubscription': 'WRITE',
            'OptInPhoneNumber': 'WRITE',
            'Subscribe': 'WRITE',
            'Unsubscribe': 'WRITE'
        },
        'AWS-Athena': {
            'BatchGetNamedQuery': 'READ',
            'BatchGetQueryExecution': 'READ',
            'ListTagsForResource': 'LIST',
            'CreateWorkGroup': 'WRITE',
            'UntagResource': 'TAGGING',
            'TagResource': 'TAGGING',
            'CancelQueryExecution': 'WRITE',
            'RunQuery': 'WRITE',
            'StartQueryExecution': 'WRITE',
            'StopQueryExecution': 'WRITE'
        },
        'AWS-Kinesis': {
            'ListTagsForStream': 'READ',
            'SubscribeToShard': 'READ',
            'AddTagsToStream': 'TAGGING',
            'RemoveTagsFromStream': 'TAGGING',
            'DecreaseStreamRetentionPeriod': 'WRTITE',
            'DeregisterStreamConsumer': 'WRITE',
            'DisableEnhancedMonitoring': 'WRITE',
            'EnableEnhancedMonitoring': 'WRITE',
            'IncreaseStreamRetentionPeriod': 'WRITE',
            'MergeShards': 'WRITE',
            'RegisterStreamConsumer': 'WRITE',
            'SplitShard': 'WRITE',
            'UpdateShardCount': 'WRITE'
        },
        'AWS-Firehose': {
            'DescribeDeliveryStream': 'LIST',
            'StartDeliveryStreamEncryption': 'WRITE',
            'StopDeliveryStreamEncryption': 'WRITE',
            'TagDeliveryStream': 'WRITE',
            'UntagDeliveryStream': 'WRITE'
        },
        'AWS-SQS': {
            'ListDeadLetterSourceQueues': 'READ',
            'ListQueueTags': 'READ',
            'ReceiveMessage': 'READ',
            'TagQueue': 'TAGGING',
            'UntagQueue': 'TAGGING',
            'PurgeQueue': 'WRITE',
            'SetQueueAttributes': 'WRITE'
        },
        'AWS-DynamoDB': {
            'BatchGetItem': 'READ',
            'ConditionCheckItem': 'READ',
            'ListStreams': 'READ',
            'ListTagsOfResource': 'READ',
            'Query': 'READ',
            'Scan': 'READ',
            'TagResource': 'TAGGING',
            'UntagResource': 'TAGGING',
            'BatchWriteItem': 'WRITE',
            'PurchaseReservedCapacityOfferings': 'WRITE',
            'RestoreTableFromBackup': 'WRITE',
            'RestoreTableToPointInTime': 'WRITE'
        },
        'AWS-EventBridge': {
            'TestEventPattern': 'READ',
            'PutRule': 'TAGGING',
            'ActivateEventSource': 'WRITE',
            'DeactivateEventSource': 'WRITE',
            'DisableRule': 'WRITE',
            'EnableRule': 'WRITE',
            'PutEvents': 'WRITE',
            'PutPartnerEvents': 'WRITE',
            'PutPermission': 'WRITE',
            'PutTargets': 'WRITE',
            'RemovePermission': 'WRITE',
            'RemoveTargets': 'WRITE',
        },
        'AWS-SES': {
            'VerifyDomainDkim': 'READ',
            'VerifyDomainIdentity': 'READ',
            'VerifyEmailAddress': 'READ',
            'VerifyEmailIdentity': 'READ',
            'CloneReceiptRuleSet': 'WRITE',
            'ReorderReceiptRuleSet': 'WRITE',
            'TestRenderTemplate': 'WRITE',
        },
        'AWS-StepFunctions': {
            'StartExecution': 'EXECUTE'
        }
    },
    'patterns': OrderedDict([
        ('^List.*$', 'LIST'),
        ('^Get.*$', 'READ'),
        ('^Create.*$', 'WRITE'),
        ('^Delete.*$', 'WRITE'),
        ('^Invoke.*$', 'WRITE'),
        ('^Publish.*$', 'WRITE'),
        ('^Put.*$', 'WRITE'),
        ('^Update.*$', 'WRITE'),
        ('^Describe.*$', 'READ'),
        ('^Change.*$', 'WRITE'),
        ('^Send.*$', 'WRITE'),
        ('^.*Permission$', 'PERMISSION'),
        ('^.*Tagging$', 'TAGGING'),
        ('^.*Tags$', 'TAGGING'),
        ('^Set.*$', 'WRITE')
    ])
}

AwsEventBridgeTags = {
    'SERVICE_REQUEST': 'AWSEventBridgeRequest',
    'ENTRIES': 'aws.eventbridge.entries'
}
