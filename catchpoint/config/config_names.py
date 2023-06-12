CATCHPOINT_APIKEY = 'catchpoint.apikey'

CATCHPOINT_DEBUG_ENABLE = 'catchpoint.debug.enable'

#############################################################################

CATCHPOINT_DISABLE = 'catchpoint.disable'
CATCHPOINT_TRACE_DISABLE = 'catchpoint.trace.disable'
CATCHPOINT_METRIC_DISABLE = 'catchpoint.metric.disable'
CATCHPOINT_LOG_DISABLE = 'catchpoint.log.disable'

#############################################################################

CATCHPOINT_APPLICATION_ID = 'catchpoint.application.id'
CATCHPOINT_APPLICATION_INSTANCE_ID = 'catchpoint.application.instanceid'
CATCHPOINT_APPLICATION_NAME = 'catchpoint.application.name'
CATCHPOINT_APPLICATION_STAGE = 'catchpoint.application.stage'
CATCHPOINT_APPLICATION_DOMAIN_NAME = 'catchpoint.application.domainname'
CATCHPOINT_APPLICATION_CLASS_NAME = 'catchpoint.application.classname'
CATCHPOINT_APPLICATION_VERSION = 'catchpoint.application.version'
CATCHPOINT_APPLICATION_TAG_PREFIX = 'catchpoint.application.tag'
CATCHPOINT_APPLICATION_REGION = 'catchpoint.application.region'

#############################################################################

CATCHPOINT_REPORT_REST_BASEURL = 'catchpoint.report.rest.baseurl'
CATCHPOINT_REPORT_CLOUDWATCH_ENABLE = 'catchpoint.report.cloudwatch.enable'
CATCHPOINT_REPORT_REST_COMPOSITE_BATCH_SIZE = 'catchpoint.report.rest.composite.batchsize'
CATCHPOINT_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE = 'catchpoint.report.cloudwatch.composite.batchsize'
CATCHPOINT_REPORT_REST_COMPOSITE_ENABLE = 'catchpoint.report.rest.composite.enable'
CATCHPOINT_REPORT_CLOUDWATCH_COMPOSITE_ENABLE = 'catchpoint.report.cloudwatch.composite.enable'
CATCHPOINT_REPORT_REST_LOCAL = 'catchpoint.report.rest.local'

#############################################################################

CATCHPOINT_LAMBDA_HANDLER = 'catchpoint.lambda.handler'

CATCHPOINT_LAMBDA_WARMUP_WARMUPAWARE = 'catchpoint.lambda.warmup.warmupaware'

CATCHPOINT_LAMBDA_TIMEOUT_MARGIN = 'catchpoint.lambda.timeout.margin'

CATCHPOINT_LAMBDA_ERROR_STACKTRACE_MASK = 'catchpoint.lambda.error.stacktrace.mask'

CATCHPOINT_TRACE_REQUEST_SKIP = 'catchpoint.trace.request.skip'
CATCHPOINT_TRACE_RESPONSE_SKIP = 'catchpoint.trace.response.skip'
CATCHPOINT_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE = 'catchpoint.lambda.trace.kinesis.request.enable'
CATCHPOINT_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE = 'catchpoint.lambda.trace.firehose.request.enable'
CATCHPOINT_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE = 'catchpoint.lambda.trace.cloudwatchlog.request.enable'

CATCHPOINT_LAMBDA_AWS_STEPFUNCTIONS = 'catchpoint.lambda.aws.stepfunctions'
CATCHPOINT_LAMBDA_AWS_APPSYNC = 'catchpoint.lambda.aws.appsync'

#############################################################################

CATCHPOINT_TRACE_INSTRUMENT_DISABLE = 'catchpoint.trace.instrument.disable'
CATCHPOINT_TRACE_INSTRUMENT_TRACEABLECONFIG = 'catchpoint.trace.instrument.traceableconfig'

#############################################################################

CATCHPOINT_TRACE_SPAN_LISTENERCONFIG = 'catchpoint.trace.span.listenerconfig'

#############################################################################

CATCHPOINT_SAMPLER_TIMEAWARE_TIMEFREQ = 'catchpoint.sampler.timeaware.timefreq'
CATCHPOINT_SAMPLER_COUNTAWARE_COUNTFREQ = 'catchpoint.sampler.countaware.countfreq'

#############################################################################

CATCHPOINT_TRACE_INTEGRATIONS_AWS_SNS_MESSAGE_MASK = 'catchpoint.trace.integrations.aws.sns.message.mask'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_SNS_TRACEINJECTION_DISABLE = 'catchpoint.trace.integrations.aws.sns.traceinjection.disable'

CATCHPOINT_TRACE_INTEGRATIONS_AWS_SQS_MESSAGE_MASK = 'catchpoint.trace.integrations.aws.sqs.message.mask'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_SQS_TRACEINJECTION_DISABLE = 'catchpoint.trace.integrations.aws.sqs.traceinjection.disable'

CATCHPOINT_TRACE_INTEGRATIONS_AWS_LAMBDA_PAYLOAD_MASK = 'catchpoint.trace.integrations.aws.lambda.payload.mask'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_LAMBDA_TRACEINJECTION_DISABLE = 'catchpoint.trace.integrations.aws.lambda.traceinjection.disable'

CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_STATEMENT_MASK = 'catchpoint.trace.integrations.aws.dynamodb.statement.mask'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE = 'catchpoint.trace.integrations.aws.dynamodb.traceinjection.enable'

CATCHPOINT_TRACE_INTEGRATIONS_AWS_ATHENA_STATEMENT_MASK = 'catchpoint.trace.integrations.aws.athena.statement.mask'

CATCHPOINT_TRACE_INTEGRATIONS_HTTP_BODY_MASK = 'catchpoint.trace.integrations.http.body.mask'
CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH = 'catchpoint.trace.integrations.http.url.depth'
CATCHPOINT_TRACE_INTEGRATIONS_HTTP_TRACEINJECTION_DISABLE = 'catchpoint.trace.integrations.http.traceinjection.disable'
CATCHPOINT_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN = 'catchpoint.trace.integrations.http.error.status.code.min'

CATCHPOINT_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK = 'catchpoint.trace.integrations.redis.command.mask'
CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK = 'catchpoint.trace.integrations.rdb.statement.mask'

CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_BODY_MASK = 'catchpoint.trace.integrations.elasticsearch.body.mask'
CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH = 'catchpoint.trace.integrations.elasticsearch.path.depth'

CATCHPOINT_TRACE_INTEGRATIONS_MONGODB_COMMAND_MASK = 'catchpoint.trace.integrations.mongodb.command.mask'

CATCHPOINT_TRACE_INTEGRATIONS_EVENTBRIDGE_DETAIL_MASK = 'catchpoint.trace.integrations.aws.eventbridge.detail.mask'

CATCHPOINT_TRACE_INTEGRATIONS_AWS_SES_MAIL_MASK = 'catchpoint.trace.integrations.aws.ses.mail.mask'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_SES_MAIL_DESTINATION_MASK = 'catchpoint.trace.integrations.aws.ses.mail.destination.mask'

CATCHPOINT_TRACE_INTEGRATIONS_HTTP_DISABLE = 'catchpoint.trace.integrations.http.disable'
CATCHPOINT_TRACE_INTEGRATIONS_RDB_DISABLE = 'catchpoint.trace.integrations.rdb.disable'
CATCHPOINT_TRACE_INTEGRATIONS_AWS_DISABLE = 'catchpoint.trace.integrations.aws.disable'
CATCHPOINT_TRACE_INTEGRATIONS_REDIS_DISABLE = 'catchpoint.trace.integrations.redis.disable'
CATCHPOINT_TRACE_INTEGRATIONS_ES_DISABLE = 'catchpoint.trace.integrations.elasticsearch.disable'
CATCHPOINT_TRACE_INTEGRATIONS_MONGO_DISABLE = 'catchpoint.trace.integrations.mongodb.disable'
CATCHPOINT_TRACE_INTEGRATIONS_SQLALCHEMY_DISABLE = 'catchpoint.trace.integrations.sqlalchemy.disable'
CATCHPOINT_TRACE_INTEGRATIONS_CHALICE_DISABLE = 'catchpoint.trace.integrations.chalice.disable'
CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_DISABLE = 'catchpoint.trace.integrations.django.disable'
CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE = 'catchpoint.trace.integrations.django.orm.disable'
CATCHPOINT_TRACE_INTEGRATIONS_FLASK_DISABLE = 'catchpoint.trace.integrations.flask.disable'
CATCHPOINT_TRACE_INTEGRATIONS_FASTAPI_DISABLE = 'catchpoint.trace.integrations.fastapi.disable'
CATCHPOINT_TRACE_INTEGRATIONS_TORNADO_DISABLE = 'catchpoint.trace.integrations.tornado.disable'

#############################################################################

CATCHPOINT_LOG_CONSOLE_DISABLE = 'catchpoint.log.console.disable'
CATCHPOINT_LOG_LOGLEVEL = 'catchpoint.log.loglevel'

#############################################################################

CATCHPOINT_LAMBDA_DEBUGGER_ENABLE = 'catchpoint.lambda.debugger.enable'
CATCHPOINT_LAMBDA_DEBUGGER_PORT = 'catchpoint.lambda.debugger.port'
CATCHPOINT_LAMBDA_DEBUGGER_LOGS_ENABLE = 'catchpoint.lambda.debugger.logs.enable'
CATCHPOINT_LAMBDA_DEBUGGER_WAIT_MAX = 'catchpoint.lambda.debugger.wait.max'
CATCHPOINT_LAMBDA_DEBUGGER_IO_WAIT = 'catchpoint.lambda.debugger.io.wait'
CATCHPOINT_LAMBDA_DEBUGGER_BROKER_PORT = 'catchpoint.lambda.debugger.broker.port'
CATCHPOINT_LAMBDA_DEBUGGER_BROKER_HOST = 'catchpoint.lambda.debugger.broker.host'
CATCHPOINT_LAMBDA_DEBUGGER_SESSION_NAME = 'catchpoint.lambda.debugger.session.name'
CATCHPOINT_LAMBDA_DEBUGGER_AUTH_TOKEN = 'catchpoint.lambda.debugger.auth.token'


#############################################################################
CATCHPOINT_TEST_RUN_ID = "catchpoint.test.run.id"
CATCHPOINT_TEST_PROJECT_ID = "catchpoint.test.project.id"
CATCHPOINT_TEST_STATUS_REPORT_FREQUENCY = "catchpoint.test.status.report.freq"
CATCHPOINT_TEST_LOG_COUNT_MAX = "catchpoint.test.log.count.max"
CATCHPOINT_TEST_SPAN_COUNT_MAX = "catchpoint.test.span.count.max" #TODO it has been not added to README.md
CATCHPOINT_TEST_ACTIVE = "catchpoint.test.active"
CATCHPOINT_TEST_DISABLE = "catchpoint.test.disable"
