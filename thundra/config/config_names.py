THUNDRA_APIKEY = 'thundra.apikey'

THUNDRA_DEBUG_ENABLE = 'thundra.agent.debug.enable'

#############################################################################

THUNDRA_DISABLE = 'thundra.agent.disable'
THUNDRA_TRACE_DISABLE = 'thundra.agent.trace.disable'
THUNDRA_METRIC_DISABLE = 'thundra.agent.metric.disable'
THUNDRA_LOG_DISABLE = 'thundra.agent.log.disable'

#############################################################################

THUNDRA_APPLICATION_ID = 'thundra.agent.application.id'
THUNDRA_APPLICATION_NAME = 'thundra.agent.application.name'
THUNDRA_APPLICATION_STAGE = 'thundra.agent.application.stage'
THUNDRA_APPLICATION_DOMAIN_NAME = 'thundra.agent.application.domainname'
THUNDRA_APPLICATION_CLASS_NAME = 'thundra.agent.application.classname'
THUNDRA_APPLICATION_VERSION = 'thundra.agent.application.version'
THUNDRA_APPLICATION_TAG_PREFIX = 'thundra.agent.application.tag.'

#############################################################################

THUNDRA_REPORT_REST_BASEURL = 'thundra.agent.report.rest.baseurl'
THUNDRA_REPORT_CLOUDWATCH_ENABLE = 'thundra.agent.report.cloudwatch.enable'
THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE = 'thundra.agent.report.rest.composite.batchsize'
THUNDRA_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE = 'thundra.agent.report.cloudwatch.composite.batchsize'
THUNDRA_REPORT_REST_COMPOSITE_ENABLE = 'thundra.agent.report.rest.composite.enable'
THUNDRA_REPORT_CLOUDWATCH_COMPOSITE_ENABLE = 'thundra.agent.report.cloudwatch.composite.enable'

#############################################################################

THUNDRA_LAMBDA_HANDLER = 'thundra.agent.lambda.handler'

THUNDRA_LAMBDA_WARMUP_WARMUPAWARE = 'thundra.agent.lambda.warmup.warmupaware'

THUNDRA_LAMBDA_TIMEOUT_MARGIN = 'thundra.agent.lambda.timeout.margin'

THUNDRA_LAMBDA_ERROR_STACKTRACE_MASK = 'thundra.agent.lambda.error.stacktrace.mask'

THUNDRA_LAMBDA_TRACE_REQUEST_SKIP = 'thundra.agent.lambda.trace.request.skip'
THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP = 'thundra.agent.lambda.trace.response.skip'
THUNDRA_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE = 'thundra.agent.lambda.trace.kinesis.request.enable'
THUNDRA_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE = 'thundra.agent.lambda.trace.firehose.request.enable'
THUNDRA_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE = 'thundra.agent.lambda.trace.cloudwatchlog.request.enable'

THUNDRA_LAMBDA_AWS_STEPFUNCTIONS = 'thundra.agent.lambda.aws.stepfunctions'

#############################################################################

THUNDRA_TRACE_INSTRUMENT_DISABLE = 'thundra.agent.trace.instrument.disable'
THUNDRA_TRACE_INSTRUMENT_TRACEABLECONFIG = 'thundra.agent.trace.instrument.traceableconfig'

#############################################################################

THUNDRA_TRACE_SPAN_LISTENERCONFIG = 'thundra.agent.trace.span.listenerconfig'

#############################################################################

THUNDRA_SAMPLER_TIMEAWARE_TIMEFREQ = 'thundra.agent.sampler.timeaware.timefreq'
THUNDRA_SAMPLER_COUNTAWARE_COUNTFREQ = 'thundra.agent.sampler.countaware.countfreq'

#############################################################################

THUNDRA_TRACE_INTEGRATIONS_AWS_SNS_MESSAGE_MASK = 'thundra.agent.trace.integrations.aws.sns.message.mask'
THUNDRA_TRACE_INTEGRATIONS_AWS_SNS_TRACEINJECTION_DISABLE = 'thundra.agent.trace.integrations.aws.sns.traceinjection.disable'

THUNDRA_TRACE_INTEGRATIONS_AWS_SQS_MESSAGE_MASK = 'thundra.agent.trace.integrations.aws.sqs.message.mask'
THUNDRA_TRACE_INTEGRATIONS_AWS_SQS_TRACEINJECTION_DISABLE = 'thundra.agent.trace.integrations.aws.sqs.traceinjection.disable'

THUNDRA_TRACE_INTEGRATIONS_AWS_LAMBDA_PAYLOAD_MASK = 'thundra.agent.trace.integrations.aws.lambda.payload.mask'
THUNDRA_TRACE_INTEGRATIONS_AWS_LAMBDA_TRACEINJECTION_DISABLE = 'thundra.agent.trace.integrations.aws.lambda.traceinjection.disable'

THUNDRA_TRACE_INTEGRATIONS_AWS_DYNAMODB_STATEMENT_MASK = 'thundra.agent.trace.integrations.aws.dynamodb.statement.mask'
THUNDRA_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE = 'thundra.agent.trace.integrations.aws.dynamodb.traceinjection.enable'

THUNDRA_TRACE_INTEGRATIONS_AWS_ATHENA_STATEMENT_MASK = 'thundra.agent.trace.integrations.aws.athena.statement.mask'

THUNDRA_TRACE_INTEGRATIONS_HTTP_BODY_MASK = 'thundra.agent.trace.integrations.http.body.mask'
THUNDRA_TRACE_INTEGRATIONS_HTTP_URL_DEPTH = 'thundra.agent.trace.integrations.http.url.depth'
THUNDRA_TRACE_INTEGRATIONS_HTTP_TRACEINJECTION_DISABLE = 'thundra.agent.trace.integrations.http.traceinjection.disable'
THUNDRA_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN = 'thundra.agent.trace.integrations.http.error.status.code.min'

THUNDRA_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK = 'thundra.agent.trace.integrations.redis.command.mask'
THUNDRA_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK = 'thundra.agent.trace.integrations.rdb.statement.mask'

THUNDRA_TRACE_INTEGRATIONS_ELASTICSEARCH_BODY_MASK = 'thundra.agent.trace.integrations.elasticsearch.body.mask'
THUNDRA_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH = 'thundra.agent.trace.integrations.elasticsearch.path.depth'

THUNDRA_TRACE_INTEGRATIONS_MONGODB_COMMAND_MASK = 'thundra.agent.trace.integrations.mongodb.command.mask'

THUNDRA_TRACE_INTEGRATIONS_EVENTBRIDGE_DETAIL_MASK = 'thundra.agent.trace.integrations.aws.eventbridge.detail.mask'

THUNDRA_TRACE_INTEGRATIONS_AWS_SES_MAIL_MASK = 'thundra.agent.trace.integrations.aws.ses.mail.mask'
THUNDRA_TRACE_INTEGRATIONS_AWS_SES_MAIL_DESTINATION_MASK = 'thundra.agent.trace.integrations.aws.ses.mail.destination.mask'

THUNDRA_TRACE_INTEGRATIONS_HTTP_DISABLE = 'thundra.agent.trace.integrations.http.disable'
THUNDRA_TRACE_INTEGRATIONS_RDB_DISABLE = 'thundra.agent.trace.integrations.rdb.disable'
THUNDRA_TRACE_INTEGRATIONS_AWS_DISABLE = 'thundra.agent.trace.integrations.aws.disable'
THUNDRA_TRACE_INTEGRATIONS_REDIS_DISABLE = 'thundra.agent.trace.integrations.redis.disable'
THUNDRA_TRACE_INTEGRATIONS_ES_DISABLE = 'thundra.agent.trace.integrations.elasticsearch.disable'
THUNDRA_TRACE_INTEGRATIONS_MONGO_DISABLE = 'thundra.agent.trace.integrations.mongodb.disable'
THUNDRA_TRACE_INTEGRATIONS_SQLALCHEMY_DISABLE = 'thundra.agent.trace.integrations.sqlalchemy.disable'
THUNDRA_TRACE_INTEGRATIONS_CHALICE_DISABLE = 'thundra.agent.trace.integrations.chalice.disable'

#############################################################################

THUNDRA_LOG_CONSOLE_DISABLE = 'thundra.agent.log.console.disable'
THUNDRA_LOG_LOGLEVEL = 'thundra.agent.log.loglevel'

#############################################################################

THUNDRA_LAMBDA_DEBUGGER_ENABLE = 'thundra.agent.lambda.debugger.enable'
THUNDRA_LAMBDA_DEBUGGER_PORT = 'thundra.agent.lambda.debugger.port'
THUNDRA_LAMBDA_DEBUGGER_LOGS_ENABLE = 'thundra.agent.lambda.debugger.logs.enable'
THUNDRA_LAMBDA_DEBUGGER_WAIT_MAX = 'thundra.agent.lambda.debugger.wait.max'
THUNDRA_LAMBDA_DEBUGGER_IO_WAIT = 'thundra.agent.lambda.debugger.io.wait'
THUNDRA_LAMBDA_DEBUGGER_BROKER_PORT = 'thundra.agent.lambda.debugger.broker.port'
THUNDRA_LAMBDA_DEBUGGER_BROKER_HOST = 'thundra.agent.lambda.debugger.broker.host'
THUNDRA_LAMBDA_DEBUGGER_SESSION_NAME = 'thundra.agent.lambda.debugger.session.name'
THUNDRA_LAMBDA_DEBUGGER_AUTH_TOKEN = 'thundra.agent.lambda.debugger.auth.token'
