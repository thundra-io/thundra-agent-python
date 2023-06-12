# Catchpoint Agent Python For Tracing

[![OpenTracing Badge](https://img.shields.io/badge/OpenTracing-enabled-blue.svg)](http://opentracing.io)
[![Pyversions](https://img.shields.io/pypi/pyversions/thundra.svg?style=flat)](https://pypi.org/project/thundra/)
[![PyPI](https://img.shields.io/pypi/v/thundra.svg)](https://pypi.org/project/thundra/)

Trace your marvelous python projects with async monitoring by [Catchpoint](https://start.thundra.io/)!

## Async Monitoring with Zero Overhead
By default, Catchpoint agent reports by making an HTTPS request. This adds an overhead to your lambda function.

Instead, you can [setup async monitoring](https://apm.docs.thundra.io/performance/zero-overhead-with-asynchronous-monitoring) in **2 minutes** and monitor your lambda functions with **zero overhead**!

## Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [No-Code Change Tracing](#no-code-change-tracing)
  - [In-Code Configuration Tracing](#in-code-configuration-tracing)
  - [Decorator](#decorator)
  - [Request Body](#request-body)
- [Frameworks](#frameworks)
- [Integrations](#integrations)
- [Log Plugin](#log-plugin)
- [Getting Help](#getting-help)
- [Opening Issues](#opening-issues)
- [All Environment Variables](#all-environment-variables)

  
## Installation

Run this command from your project directory:
```bash
pip install catchpoint -t .
```

## Configuration
You can configure Catchpoint using **environment variables** or **module initialization parameters**.

Environment variables have **higher precedence** over initialization parameters.

Check out the [configuration part](https://docs.thundra.io/python/configuration-options) of our docs for more detailed information.

#### 1. Most Useful Environment variables

| Name                                               | Type   |          Default Value           |
|:---------------------------------------------------|:------:|:--------------------------------:|
| CATCHPOINT_APIKEY                                  | string |                -                 |
| CATCHPOINT_APPLICATION_NAME                        | string |                -                 |
| CATCHPOINT_APPLICATION_STAGE                       | string |                -                 |
| CATCHPOINT_TRACE_DISABLE                           |  bool  |              false               |
| CATCHPOINT_METRIC_DISABLE                          |  bool  |              false               |
| CATCHPOINT_LOG_DISABLE                             |  bool  |              false               |
| CATCHPOINT_TRACE_REQUEST_SKIP                      |  bool  |              false               |
| CATCHPOINT_TRACE_RESPONSE_SKIP                     |  bool  |              false               |
| CATCHPOINT_LAMBDA_TIMEOUT_MARGIN                   |  int   |               200                |
| CATCHPOINT_REPORT_REST_BASEURL                     | string | https://collector.thundra.io/v1  |
| CATCHPOINT_TEST_RUN_ID                             | string |                -                 |
| CATCHPOINT_TEST_PROJECT_ID                         | string |                -                 |
| CATCHPOINT_TEST_STATUS_REPORT_FREQUENCY            |  int   |              30sec               |
| CATCHPOINT_TEST_LOG_COUNT_MAX                      |  int   |               100                |



#### 2. Object initialization parameters

| Name            | Type   | Default Value |
|:----------------|:------:|:-------------:|
| api_key         | string |       -       |
| disable_trace   |  bool  |     False     |
| disable_metric  |  bool  |     False     |
| disable_log     |  bool  |     False     |

## Usage

### No-Code Change Tracing

The simplest way to auto trace configuration of all your endpoints into project by setting following environment variables:
```sh
export CATCHPOINT_APIKEY=<your_catchpoint_api_key>
export CATCHPOINT_APPLICATION_NAME=<your_application_name>
<python command>
```

For illustration of Fastapi:
```sh
export CATCHPOINT_APIKEY=<your_catchpoint_api_key>
export CATCHPOINT_APPLICATION_NAME=fastapi-prod
uvicorn main:app --reload
```

For `Dockerfile`, you just replace `export` with `ENV`.

You can see the list of no-code change [supported frameworks](#frameworks)

### In-Code Configuration Tracing

Another simple alternative is to copy the snippet into your code before your app created:
```python
import catchpoint

catchpoint.configure(
     options={
         "config": {
             "catchpoint.apikey": <your_catchpoint_api_key>,
             "catchpoint.application.name": <your_application_name>
         }
     }
)
```

To run on your framework please refer to [supported frameworks](#frameworks)


### Decorator

Just import this module, pass your api key to it and use our decorator to wrap your handler:
```python
import catchpoint

catchpoint.configure(
     options={
         "config": {
             "catchpoint.apikey": <your_catchpoint_api_key>,
             "catchpoint.agent.application.name": <your_application_name>
         }
     }
)

@catchpoint.<framework_wrapper>
def handler(event, context):
    print("Hello Catchpoint!")
```

OR

```sh
export CATCHPOINT_APIKEY=<your_catchpoint_api_key>
export CATCHPOINT_APPLICATION_NAME=<your_application_name>
```

```python
import catchpoint

@catchpoint.<framework_wrapper>
def handler(event, context):
    print("Hello Catchpoint!")
```

**NOTES**

- To run on your framework please refer to [supported frameworks](#frameworks)
- You should disable framework that you use by using environment variable or in-code configuration. Explanations can
be found in corresponding framework section.

###  Request Body

Normally catchpoint does not get your project's requests' body. In order to see request body on tracing data, following environment variable shall be set besides api key and application name:

```sh
export CATCHPOINT_TRACE_REQUEST_SKIP=True
```

OR

```python
import catchpoint

catchpoint.configure(
     options={
         "config": {
             "catchpoint.apikey": <your_catchpoint_api_key>,
             "catchpoint.application.name": <your_application_name>,
			 "catchpoint.trace.request.skip": True
         }
     }
)
```

## Frameworks

The following frameworks are supported by Catchpoint:

|Framework                               |Supported Version          |Auto-tracing Supported                               |
|----------------------------------------|---------------------------|-----------------------------------------------------|
|[AWS Lambda](#aws-lambda)               |All                        |<ul><li>- [x] </li></ul>                             |
|[Django](#django)                       |`>=1.11`                   |<ul><li>- [x] </li></ul>                             |
|[Flask](#flask)                         |`>=0.5`                    |<ul><li>- [x] </li></ul>                             |
|[Fastapi](#fastapi)                     |`>=0.62.0`                 |<ul><li>- [x] </li></ul>                             |
|[Chalice](#chalice)                     |`>=1.0.0`                  |<ul><li>- [x] </li></ul>                             |
|[Tornado](#tornado)                     |`>=6.0.0`                  |<ul><li>- [x] </li></ul>                             |

### AWS Lambda

Tracing Lambda functions:

1. Check our [integration document on web site](https://apm.docs.thundra.io/python/integration-options)

**NOTES**

- Make sure to choose just one of the methods from integration document above.
- For decorator tracing method:
    1. Set `CATCHPOINT_APIKEY` and other configurations if needed as no-code change or in-code change sytle.
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.lambda_wrapper`.
- In order to activate *AWS Step Functions* trace, `CATCHPOINT_LAMBDA_AWS_STEPFUNCTIONS` environment variable should be set `true`.
- In order to activate *AWS AppSync* trace, `CATCHPOINT_LAMBDA_AWS_APPSYNC` environment variable should be set `true`.
- For other integrations' configuration, please take a look environment variables table at the end.

### Django

Tracing Django application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)

Code snippet in [In-Code Configuration Tracing](#in-code-configuration-tracing) should be added into `settings.py` file.
To trace django database processes, following environment variables shall be set to false:

- [No-Code Change Tracing](#no-code-change-tracing):
    
    ```sh
    export CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE=false
    export CATCHPOINT_TRACE_INTEGRATIONS_RDB_DISABLE=false
    ```

- [In-Code Configuration Tracing](#in-code-configuration-tracing):

    ```python
    import catchpoint

    catchpoint.configure(
        options={
            "config": {
                "catchpoint.apikey": <your_catchpoint_api_key>,
                "catchpoint.application.name": <your_application_name>,
                "catchpoint.trace.integrations.django.orm.disable": False,
                "catchpoint.trace.integrations.rdb.disable": False
            }
        }
    )
    ```


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable catchpoint django instrumentation by using `CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_DISABLE` or its corresponding in-code configuration. 
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.django_wrapper`.

### Flask

Tracing Flask application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)

Code snippet in [In-Code Configuration Tracing](#in-code-configuration-tracing) should be added into `app.py` file before
application is initialized.

**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable catchpoint flask instrumentation by using `CATCHPOINT_TRACE_INTEGRATIONS_FLASK_DISABLE` or its corresponding in-code configuration. 
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.flask_wrapper`.

### Fastapi

Tracing Fastapi application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator) by adding fastapi.Request as an parameter to your function if not exists.


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable catchpoint fastapi instrumentation by using `CATCHPOINT_TRACE_INTEGRATIONS_FASTAPI_DISABLE` or its corresponding in-code configuration. 
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.fastapi_wrapper`.
- Fastapi has been supported for python 3.7 and above.

### Chalice

Tracing Chalice application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable catchpoint chalice instrumentation by using `CATCHPOINT_TRACE_INTEGRATIONS_CHALICE_DISABLE` or its corresponding in-code configuration. 
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.chalice_wrapper`.


### Tornado

Tracing Tornado application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)


**NOTES**

- Make sure to choose just one of the methods.
- Tornado has been supported for python 3.7 and above.
- For decorator tracing method:
    1. Disable catchpoint tornado instrumentation by using `CATCHPOINT_TRACE_INTEGRATIONS_TORNADO_DISABLE` or its corresponding in-code configuration. 
    2. Change `@catchpoint.<framework_wrapper>` by `@catchpoint.tornado_wrapper`.


## Integrations

Catchpoint provides out-of-the-box instrumentation (tracing) for following libraries.

|Library             |Supported Version          |
|--------------------|---------------------------|
|logging             |Fully supported            |
|requests            |`>=2.0.0`                  |
|redis               |`>=2.10.0`                 |
|pymongo             |`>=3.0.0`                  |
|PyMySQL             |`>=0.7.0`                  |
|MySQLdb             |`>=1.0.0`                  |
|psycopg2            |`>=2.2.0`                  |
|botocore (boto3)    |`>=1.4.0`                  |
|SQLAlchemy          |`>=1.2.0`                  |
|elasticsearch       |`>=0.4.1`                  |
|aiohttp             |`>=1.1.5`                  |


## Log Plugin
Log plugin is added by default, but in order to enable it, you should add `CatchpointLogHandler` to your logger.

You can either add it via logging.conf or add during getting logger object.

#### Configure via logging.conf
An example of configuration file is as follows:

```
[loggers]
keys=root

[handlers]
keys=catchpointHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=NOTSET
handlers=catchpointHandler

[handler_catchpointHandler]
class=CatchpointLogHandler
level=NOTSET
formatter=simpleFormatter
args=()

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
```

#### Configure during getting logger object
You should add the followings after getting the logger object:
```python
handler = CatchpointLogHandler()
logger.addHandler(handler)
...
logger.removeHandler(handler)
```

## Getting Help

If you have any issue around using the library or the product, please don't hesitate to:

* Use the [documentation](https://apm.docs.thundra.io/python/integration-options).
* Open an issue in GitHub.
* Join our python slack channel.


## Opening Issues

For any problem you encounter while using catchpoint, Please feel free to contact us via github issue or our python slack channel. 

When opening a new issue, please provide as much information about the environment:
* Library version, Python runtime version, dependencies, operation system with version etc.
* Snippet of the usage.
* A reproducible example can really help.

The GitHub issues are intended for bug reports and feature requests.


## All Environment Variables

Following table shows all environment variables of [No-Code Change Tracing](#no-code-change-tracing) and their [In-Code Configuration Tracing](#in-code-configuration-tracing) equivalent.


| Environment Variable Name                                                   | [In-Code Configuration Tracing](#in-code-configuration-tracing) Name |
|:----------------------------------------------------------------------------|:---------------------------------------------------------------------|
| CATCHPOINT_APIKEY                                                           | catchpoint.apikey                                                    |
| CATCHPOINT_DEBUG_ENABLE                                                     | catchpoint.debug.enable                                              |
| CATCHPOINT_DISABLE                                                          | catchpoint.disable                                                   | 
| CATCHPOINT_TRACE_DISABLE                                                    | catchpoint.trace.disable                                             |
| CATCHPOINT_METRIC_DISABLE                                                   | catchpoint.metric.disable                                            |
| CATCHPOINT_LOG_DISABLE                                                      | catchpoint.log.disable                                               |
| CATCHPOINT_APPLICATION_ID                                                   | catchpoint.application.id                                            |
| CATCHPOINT_APPLICATION_INSTANCE_ID                                          | catchpoint.application.instanceid                                    |
| CATCHPOINT_APPLICATION_NAME                                                 | catchpoint.application.name                                          |
| CATCHPOINT_APPLICATION_STAGE                                                | catchpoint.application.stage                                      |
| CATCHPOINT_APPLICATION_DOMAIN_NAME                                          | catchpoint.application.domainname                                 |
| CATCHPOINT_APPLICATION_CLASS_NAME                                           | catchpoint.application.classname                                  |
| CATCHPOINT_APPLICATION_VERSION                                              | catchpoint.application.version                                    |
| CATCHPOINT_APPLICATION_TAG_PREFIX                                           | catchpoint.application.tag                                        |
| CATCHPOINT_APPLICATION_REGION                                               | catchpoint.application.region                                     |
| CATCHPOINT_REPORT_REST_BASEURL                                              | catchpoint.report.rest.baseurl                                    |
| CATCHPOINT_REPORT_CLOUDWATCH_ENABLE                                         | catchpoint.report.cloudwatch.enable                               |
| CATCHPOINT_REPORT_REST_COMPOSITE_BATCH_SIZE                                 | catchpoint.report.rest.composite.batchsize                        |
| CATCHPOINT_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE                           | catchpoint.report.cloudwatch.composite.batchsize                  |
| CATCHPOINT_REPORT_REST_COMPOSITE_ENABLE                                     | catchpoint.report.rest.composite.enable                           |
| CATCHPOINT_REPORT_CLOUDWATCH_COMPOSITE_ENABLE                               | catchpoint.report.cloudwatch.composite.enable                     | 
| CATCHPOINT_REPORT_REST_LOCAL                                                | catchpoint.report.rest.local                                      |
| CATCHPOINT_LAMBDA_HANDLER                                                   | catchpoint.lambda.handler                                         |
| CATCHPOINT_LAMBDA_WARMUP_WARMUPAWARE                                        | catchpoint.lambda.warmup.warmupaware                              |
| CATCHPOINT_LAMBDA_TIMEOUT_MARGIN                                            | catchpoint.lambda.timeout.margin                                  |
| CATCHPOINT_LAMBDA_ERROR_STACKTRACE_MASK                                     | catchpoint.lambda.error.stacktrace.mask                           |
| CATCHPOINT_TRACE_REQUEST_SKIP                                               | catchpoint.trace.request.skip                                     |
| CATCHPOINT_TRACE_RESPONSE_SKIP                                              | catchpoint.trace.response.skip                                    |
| CATCHPOINT_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE                              | catchpoint.lambda.trace.kinesis.request.enable                    |
| CATCHPOINT_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE                             | catchpoint.lambda.trace.firehose.request.enable                   |
| CATCHPOINT_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE                        | catchpoint.lambda.trace.cloudwatchlog.request.enable              |
| CATCHPOINT_LAMBDA_AWS_STEPFUNCTIONS                                         | catchpoint.lambda.aws.stepfunctions                               |
| CATCHPOINT_LAMBDA_AWS_APPSYNC                                               | catchpoint.lambda.aws.appsync                                     |
| CATCHPOINT_TRACE_INSTRUMENT_DISABLE                                         | catchpoint.trace.instrument.disable                               |
| CATCHPOINT_TRACE_INSTRUMENT_TRACEABLECONFIG                                 | catchpoint.trace.instrument.traceableconfig                       |
| CATCHPOINT_TRACE_SPAN_LISTENERCONFIG                                        | catchpoint.trace.span.listenerconfig                              |
| CATCHPOINT_SAMPLER_TIMEAWARE_TIMEFREQ                                       | catchpoint.sampler.timeaware.timefreq                             |
| CATCHPOINT_SAMPLER_COUNTAWARE_COUNTFREQ                                     | catchpoint.sampler.countaware.countfreq                           |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SNS_MESSAGE_MASK                          | catchpoint.trace.integrations.aws.sns.message.mask                |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SNS_TRACEINJECTION_DISABLE                | catchpoint.trace.integrations.aws.sns.traceinjection.disable      |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SQS_MESSAGE_MASK                          | catchpoint.trace.integrations.aws.sqs.message.mask                |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SQS_TRACEINJECTION_DISABLE                | catchpoint.trace.integrations.aws.sqs.traceinjection.disable      |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_LAMBDA_PAYLOAD_MASK                       | catchpoint.trace.integrations.aws.lambda.payload.mask             |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_LAMBDA_TRACEINJECTION_DISABLE             | catchpoint.trace.integrations.aws.lambda.traceinjection.disable   |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_STATEMENT_MASK                   | catchpoint.trace.integrations.aws.dynamodb.statement.mask         |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE            | catchpoint.trace.integrations.aws.dynamodb.traceinjection.enable  |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_ATHENA_STATEMENT_MASK                     | catchpoint.trace.integrations.aws.athena.statement.mask           |
| CATCHPOINT_TRACE_INTEGRATIONS_HTTP_BODY_MASK                                | catchpoint.trace.integrations.http.body.mask                      |
| CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH                                | catchpoint.trace.integrations.http.url.depth                      |
| CATCHPOINT_TRACE_INTEGRATIONS_HTTP_TRACEINJECTION_DISABLE                   | catchpoint.trace.integrations.http.traceinjection.disable         |
| CATCHPOINT_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN                    | catchpoint.trace.integrations.http.error.status.code.min          |
| CATCHPOINT_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK                            | catchpoint.trace.integrations.redis.command.mask                  |
| CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK                            | catchpoint.trace.integrations.rdb.statement.mask                  |
| CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_BODY_MASK                       | catchpoint.trace.integrations.elasticsearch.body.mask             |
| CATCHPOINT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH                      | catchpoint.trace.integrations.elasticsearch.path.depth            |
| CATCHPOINT_TRACE_INTEGRATIONS_MONGODB_COMMAND_MASK                          | catchpoint.trace.integrations.mongodb.command.mask                |
| CATCHPOINT_TRACE_INTEGRATIONS_EVENTBRIDGE_DETAIL_MASK                       | catchpoint.trace.integrations.aws.eventbridge.detail.mask         |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SES_MAIL_MASK                             | catchpoint.trace.integrations.aws.ses.mail.mask                   |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_SES_MAIL_DESTINATION_MASK                 | catchpoint.trace.integrations.aws.ses.mail.destination.mask       |
| CATCHPOINT_TRACE_INTEGRATIONS_HTTP_DISABLE                                  | catchpoint.trace.integrations.http.disable                        |
| CATCHPOINT_TRACE_INTEGRATIONS_RDB_DISABLE                                   | catchpoint.trace.integrations.rdb.disable                         |
| CATCHPOINT_TRACE_INTEGRATIONS_AWS_DISABLE                                   | catchpoint.trace.integrations.aws.disable                         |
| CATCHPOINT_TRACE_INTEGRATIONS_REDIS_DISABLE                                 | catchpoint.trace.integrations.redis.disable                       |
| CATCHPOINT_TRACE_INTEGRATIONS_ES_DISABLE                                    | catchpoint.trace.integrations.elasticsearch.disable               |
| CATCHPOINT_TRACE_INTEGRATIONS_MONGO_DISABLE                                 | catchpoint.trace.integrations.mongodb.disable                     |
| CATCHPOINT_TRACE_INTEGRATIONS_SQLALCHEMY_DISABLE                            | catchpoint.trace.integrations.sqlalchemy.disable                  |
| CATCHPOINT_TRACE_INTEGRATIONS_CHALICE_DISABLE                               | catchpoint.trace.integrations.chalice.disable                     |
| CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_DISABLE                                | catchpoint.trace.integrations.django.disable                      |
| CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE                            | catchpoint.trace.integrations.django.orm.disable                  |
| CATCHPOINT_TRACE_INTEGRATIONS_FLASK_DISABLE                                 | catchpoint.trace.integrations.flask.disable                       |
| CATCHPOINT_TRACE_INTEGRATIONS_FASTAPI_DISABLE                               | catchpoint.trace.integrations.fastapi.disable                     | 
| CATCHPOINT_LOG_CONSOLE_DISABLE                                              | catchpoint.log.console.disable                                    |
| CATCHPOINT_LOG_LOGLEVEL                                                     | catchpoint.log.loglevel                                           |
| CATCHPOINT_LAMBDA_DEBUGGER_ENABLE                                           | catchpoint.lambda.debugger.enable                                 |
| CATCHPOINT_LAMBDA_DEBUGGER_PORT                                             | catchpoint.lambda.debugger.port                                   |
| CATCHPOINT_LAMBDA_DEBUGGER_LOGS_ENABLE                                      | catchpoint.lambda.debugger.logs.enable                            |
| CATCHPOINT_LAMBDA_DEBUGGER_WAIT_MAX                                         | catchpoint.lambda.debugger.wait.max                               |
| CATCHPOINT_LAMBDA_DEBUGGER_IO_WAIT                                          | catchpoint.lambda.debugger.io.wait                                |
| CATCHPOINT_LAMBDA_DEBUGGER_BROKER_PORT                                      | catchpoint.lambda.debugger.broker.port                            |
| CATCHPOINT_LAMBDA_DEBUGGER_BROKER_HOST                                      | catchpoint.lambda.debugger.broker.host                            |
| CATCHPOINT_LAMBDA_DEBUGGER_SESSION_NAME                                     | catchpoint.lambda.debugger.session.name                           |
| CATCHPOINT_LAMBDA_DEBUGGER_AUTH_TOKEN                                       | catchpoint.lambda.debugger.auth.token                             |
| CATCHPOINT_TEST_RUN_ID                                                      | catchpoint.test.run.id                                            |
| CATCHPOINT_TEST_PROJECT_ID                                                  | catchpoint.test.project.id                                        | 
| CATCHPOINT_TEST_STATUS_REPORT_FREQUENCY                                     | catchpoint.test.status.report.freq                                | 
| CATCHPOINT_TEST_LOG_COUNT_MAX                                               | catchpoint.test.log.count.max                                     || 
 CATCHPOINT_TEST_DISABLE                                                      | catchpoint.test.disable                                           |
