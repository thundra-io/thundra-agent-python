# Thundra Agent Python For Tracing

[![OpenTracing Badge](https://img.shields.io/badge/OpenTracing-enabled-blue.svg)](http://opentracing.io)
[![Pyversions](https://img.shields.io/pypi/pyversions/thundra.svg?style=flat)](https://pypi.org/project/thundra/)
[![PyPI](https://img.shields.io/pypi/v/thundra.svg)](https://pypi.org/project/thundra/)

Trace your marvelous python projects with async monitoring by [Thundra](https://start.thundra.io/)!

## Async Monitoring with Zero Overhead
By default, Thundra agent reports by making an HTTPS request. This adds an overhead to your lambda function.

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
- [Thundra Foresight](#thundra-foresight)
    - [Activating Thundra Foresight](#activating-thundra-foresight)
- [Getting Help](#getting-help)
- [Opening Issues](#opening-issues)
- [All Environment Variables](#all-environment-variables)

  
## Installation

Run this command from your project directory:
```bash
pip install thundra -t .
```

## Configuration
You can configure Thundra using **environment variables** or **module initialization parameters**.

Environment variables have **higher precedence** over initialization parameters.

Check out the [configuration part](https://docs.thundra.io/python/configuration-options) of our docs for more detailed information.

#### 1. Most Useful Environment variables

| Name                                                | Type   |          Default Value           |
|:----------------------------------------------------|:------:|:--------------------------------:|
| THUNDRA_APIKEY                                      | string |                -                 |
| THUNDRA_AGENT_APPLICATION_NAME                      | string |                -                 |
| THUNDRA_AGENT_APPLICATION_STAGE                     | string |                -                 |
| THUNDRA_AGENT_TRACE_DISABLE                         |  bool  |              false               |
| THUNDRA_AGENT_METRIC_DISABLE                        |  bool  |              false               |
| THUNDRA_AGENT_LOG_DISABLE                           |  bool  |              false               |
| THUNDRA_AGENT_TRACE_REQUEST_SKIP                    |  bool  |              false               |
| THUNDRA_AGENT_TRACE_RESPONSE_SKIP                   |  bool  |              false               |
| THUNDRA_AGENT_LAMBDA_TIMEOUT_MARGIN                 |  int   |               200                |
| THUNDRA_AGENT_REPORT_REST_BASEURL                   | string | https://collector.thundra.io/v1  |
| THUNDRA_AGENT_TEST_RUN_ID                           | string |                -                 |
| THUNDRA_AGENT_TEST_PROJECT_ID                       | string |                -                 |
| THUNDRA_AGENT_TEST_STATUS_REPORT_FREQUENCY          |  int   |              30sec               |
| THUNDRA_AGENT_TEST_LOG_COUNT_MAX                    |  int   |               100                |



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
export THUNDRA_APIKEY=<your_thundra_api_key>
export THUNDRA_AGENT_APPLICATION_NAME=<your_application_name>
<python command>
```

For illustration of Fastapi:
```sh
export THUNDRA_APIKEY=<your_thundra_api_key>
export THUNDRA_AGENT_APPLICATION_NAME=fastapi-prod
uvicorn main:app --reload
```

For `Dockerfile`, you just replace `export` with `ENV`.

You can see the list of no-code change [supported frameworks](#frameworks)

### In-Code Configuration Tracing

Another simple alternative is to copy the snippet into your code before your app created:
```python
import thundra

thundra.configure(
     options={
         "config": {
             "thundra.apikey": <your_thundra_api_key>,
             "thundra.agent.application.name": <your_application_name>
         }
     }
)
```

To run on your framework please refer to [supported frameworks](#frameworks)


### Decorator

Just import this module, pass your api key to it and use our decorator to wrap your handler:
```python
import thundra

thundra.configure(
     options={
         "config": {
             "thundra.apikey": <your_thundra_api_key>,
             "thundra.agent.application.name": <your_application_name>
         }
     }
)

@thundra.<framework_wrapper>
def handler(event, context):
    print("Hello Thundra!")
```

OR

```sh
export THUNDRA_APIKEY=<your_thundra_api_key>
export THUNDRA_AGENT_APPLICATION_NAME=<your_application_name>
```

```python
import thundra

@thundra.<framework_wrapper>
def handler(event, context):
    print("Hello Thundra!")
```

**NOTES**

- To run on your framework please refer to [supported frameworks](#frameworks)
- You should disable framework that you use by using environment variable or in-code configuration. Explanations can
be found in corresponding framework section.

###  Request Body

Normally thundra does not get your project's requests' body. In order to see request body on tracing data, following environment variable shall be set besides api key and application name:

```sh
export THUNDRA_AGENT_TRACE_REQUEST_SKIP=True
```

OR

```python
import thundra

thundra.configure(
     options={
         "config": {
             "thundra.apikey": <your_thundra_api_key>,
             "thundra.agent.application.name": <your_application_name>,
			 "thundra.agent.trace.request.skip": True
         }
     }
)
```

## Frameworks

The following frameworks are supported by Thundra:

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
    1. Set `THUNDRA_APIKEY` and other configurations if needed as no-code change or in-code change sytle.
    2. Change `@thundra.<framework_wrapper>` by `@thundra.lambda_wrapper`.
- In order to activate *AWS Step Functions* trace, `THUNDRA_AGENT_LAMBDA_AWS_STEPFUNCTIONS` environment variable should be set `true`.
- In order to activate *AWS AppSync* trace, `THUNDRA_AGENT_LAMBDA_AWS_APPSYNC` environment variable should be set `true`.
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
    export THUNDRA_AGENT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE=false
    export THUNDRA_AGENT_TRACE_INTEGRATIONS_RDB_DISABLE=false
    ```

- [In-Code Configuration Tracing](#in-code-configuration-tracing):

    ```python
    import thundra

    thundra.configure(
        options={
            "config": {
                "thundra.apikey": <your_thundra_api_key>,
                "thundra.agent.application.name": <your_application_name>,
                "thundra.agent.trace.integrations.django.orm.disable": False,
                "thundra.agent.trace.integrations.rdb.disable": False
            }
        }
    )
    ```


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable thundra django instrumentation by using `THUNDRA_AGENT_TRACE_INTEGRATIONS_DJANGO_DISABLE` or its corresponding in-code configuration. 
    2. Change `@thundra.<framework_wrapper>` by `@thundra.django_wrapper`.

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
    1. Disable thundra flask instrumentation by using `THUNDRA_AGENT_TRACE_INTEGRATIONS_FLASK_DISABLE` or its corresponding in-code configuration. 
    2. Change `@thundra.<framework_wrapper>` by `@thundra.flask_wrapper`.

### Fastapi

Tracing Fastapi application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator) by adding fastapi.Request as an parameter to your function if not exists.


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method:
    1. Disable thundra fastapi instrumentation by using `THUNDRA_AGENT_TRACE_INTEGRATIONS_FASTAPI_DISABLE` or its corresponding in-code configuration. 
    2. Change `@thundra.<framework_wrapper>` by `@thundra.fastapi_wrapper`.
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
    1. Disable thundra chalice instrumentation by using `THUNDRA_AGENT_TRACE_INTEGRATIONS_CHALICE_DISABLE` or its corresponding in-code configuration. 
    2. Change `@thundra.<framework_wrapper>` by `@thundra.chalice_wrapper`.


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
    1. Disable thundra tornado instrumentation by using `THUNDRA_AGENT_TRACE_INTEGRATIONS_TORNADO_DISABLE` or its corresponding in-code configuration. 
    2. Change `@thundra.<framework_wrapper>` by `@thundra.tornado_wrapper`.


## Integrations

Thundra provides out-of-the-box instrumentation (tracing) for following libraries.

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
Log plugin is added by default, but in order to enable it, you should add `ThundraLogHandler` to your logger.

You can either add it via logging.conf or add during getting logger object.

#### Configure via logging.conf
An example of configuration file is as follows:

```
[loggers]
keys=root

[handlers]
keys=thundraHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=NOTSET
handlers=thundraHandler

[handler_thundraHandler]
class=ThundraLogHandler
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
handler = ThundraLogHandler()
logger.addHandler(handler)
...
logger.removeHandler(handler)
```

## Thundra Foresight

Foresight is a project powered by Thundra agent to show every detail for test runs. For know, it only supports pytest. Although Its automatically enabled after installing Thundra as 'pip install thundra', you need to set THUNDRA_APIKEY and THUNDRA_AGENT_TEST_PROJECT_ID as described below. 

### Activating Thundra Foresight

- Firstly, setting up environment for Thundra. There are three ways to do it.

    1. Setting THUNDRA_APIKEY and THUNDRA_AGENT_TEST_PROJECT_ID as environment variable.

    ```sh
    export THUNDRA_APIKEY=<your_apikey>
    export THUNDRA_AGENT_TEST_PROJECT_ID=<your_test_project_id>
    ```

    2.  "thundra_apikey " and "thundra_agent_test_project_id" in you .env file. Then, loaded them in conftest.py file like:

    ```.env
        thundra_apikey =<your_apikey>
        thundra_agent_test_project_id = <your_test_project_id>
    ```

    ```conftest.py
        # This method requires python >= 3.5
        from pathlib import Path

        from dotenv import load_dotenv

        env_path = Path(<your_env_file_name>)
        load_dotenv(dotenv_path=env_path)
    ```

    3. Importing Thundra in conftest file and configure it.

    ```conftest.py
        import thundra

        thundra.configure(
            options={
                "config": {
                    "thundra.apikey": <your_apikey>,
                    "thundra.agent.test.project.id": <your_test_project_id>
                }
            }
        )
    ```

### Deactivating Thundra Foresight

- There are three ways to deactivate Thundra Foresight for pytest:

    1. Run pytest with --thundra_disable command on terminal for specific pytest run.
    ```sh
        pytest --thundra_disable <your_tests_path>
    ```

    2. Modifying any configuration file read by pytest(pytest.ini, setup.cfg, pyproject.toml etc.) 
    Please read carefully pytest official documentation for configuration files.
    ```pytest.ini
        [pytest]
        thundra_disable = 1
    ```
    or
    ```project.toml
        [tool.pytest.ini_options]
        thundra_disable = 1
    ```
    
    3. Setting THUNDRA_AGENT_TEST_DISABLE=True as environment variable.

**NOTES**

- All Thundra agent features are valid in Foresight. It's default enabled. If you see more information about your test cases, you can visit Thundra APM. If you want to disable thundra agent for tracing, you can set "THUNDRA_AGENT_DISABLE"  as environment variable, "thundra_agent_disable" in .env file or "thundra.agent.disable" into thundra.configure() to True as describing above.

## Getting Help

If you have any issue around using the library or the product, please don't hesitate to:

* Use the [documentation](https://apm.docs.thundra.io/python/integration-options).
* Open an issue in GitHub.
* Join our python slack channel.


## Opening Issues

For any problem you encounter while using thundra, Please feel free to contact us via github issue or our python slack channel. 

When opening a new issue, please provide as much information about the environment:
* Library version, Python runtime version, dependencies, operation system with version etc.
* Snippet of the usage.
* A reproducible example can really help.

The GitHub issues are intended for bug reports and feature requests.


## All Environment Variables

Following table shows all environment variables of [No-Code Change Tracing](#no-code-change-tracing) and their [In-Code Configuration Tracing](#in-code-configuration-tracing) equivalent.


| Environment Variable Name                                        |  [In-Code Configuration Tracing](#in-code-configuration-tracing) Name     |
|:-----------------------------------------------------------------|:--------------------------------------------------------------------------|
| THUNDRA_APIKEY                                                   | thundra.apikey                                                            |
| THUNDRA_AGENT_DEBUG_ENABLE                                             | thundra.agent.debug.enable                                                |
| THUNDRA_AGENT_DISABLE                                                  | thundra.agent.disable                                                     | 
| THUNDRA_AGENT_TRACE_DISABLE                                            | thundra.agent.trace.disable                                               |
| THUNDRA_AGENT_METRIC_DISABLE                                           | thundra.agent.metric.disable                                              |
| THUNDRA_AGENT_LOG_DISABLE                                              | thundra.agent.log.disable                                                 |
| THUNDRA_AGENT_APPLICATION_ID                                           | thundra.agent.application.id                                              |
| THUNDRA_AGENT_APPLICATION_INSTANCE_ID                                  | thundra.agent.application.instanceid                                      |
| THUNDRA_AGENT_APPLICATION_NAME                                         | thundra.agent.application.name                                            |
| THUNDRA_AGENT_APPLICATION_STAGE                                        | thundra.agent.application.stage                                           |
| THUNDRA_AGENT_APPLICATION_DOMAIN_NAME                                  | thundra.agent.application.domainname                                      |
| THUNDRA_AGENT_APPLICATION_CLASS_NAME                                   | thundra.agent.application.classname                                       |
| THUNDRA_AGENT_APPLICATION_VERSION                                      | thundra.agent.application.version                                         |
| THUNDRA_AGENT_APPLICATION_TAG_PREFIX                                   | thundra.agent.application.tag                                      |
| THUNDRA_AGENT_APPLICATION_REGION                                       | thundra.agent.application.region                                          |
| THUNDRA_AGENT_REPORT_REST_BASEURL                                      | thundra.agent.report.rest.baseurl                                         |
| THUNDRA_AGENT_REPORT_CLOUDWATCH_ENABLE                                 | thundra.agent.report.cloudwatch.enable                                    |
| THUNDRA_AGENT_REPORT_REST_COMPOSITE_BATCH_SIZE                         | thundra.agent.report.rest.composite.batchsize                             |
| THUNDRA_AGENT_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE                   | thundra.agent.report.cloudwatch.composite.batchsize                       |
| THUNDRA_AGENT_REPORT_REST_COMPOSITE_ENABLE                             | thundra.agent.report.rest.composite.enable                                |
| THUNDRA_AGENT_REPORT_CLOUDWATCH_COMPOSITE_ENABLE                       | thundra.agent.report.cloudwatch.composite.enable                          | 
| THUNDRA_AGENT_REPORT_REST_LOCAL                                        | thundra.agent.report.rest.local                                           |
| THUNDRA_AGENT_LAMBDA_HANDLER                                           | thundra.agent.lambda.handler                                              |
| THUNDRA_AGENT_LAMBDA_WARMUP_WARMUPAWARE                                | thundra.agent.lambda.warmup.warmupaware                                   |
| THUNDRA_AGENT_LAMBDA_TIMEOUT_MARGIN                                    | thundra.agent.lambda.timeout.margin                                       |
| THUNDRA_AGENT_LAMBDA_ERROR_STACKTRACE_MASK                             | thundra.agent.lambda.error.stacktrace.mask                                |
| THUNDRA_AGENT_TRACE_REQUEST_SKIP                                       | thundra.agent.trace.request.skip                                          |
| THUNDRA_AGENT_TRACE_RESPONSE_SKIP                                      | thundra.agent.trace.response.skip                                         |
| THUNDRA_AGENT_LAMBDA_TRACE_KINESIS_REQUEST_ENABLE                      | thundra.agent.lambda.trace.kinesis.request.enable                         |
| THUNDRA_AGENT_LAMBDA_TRACE_FIREHOSE_REQUEST_ENABLE                     | thundra.agent.lambda.trace.firehose.request.enable                        |
| THUNDRA_AGENT_LAMBDA_TRACE_CLOUDWATCHLOG_REQUEST_ENABLE                | thundra.agent.lambda.trace.cloudwatchlog.request.enable                   |
| THUNDRA_AGENT_LAMBDA_AWS_STEPFUNCTIONS                                 | thundra.agent.lambda.aws.stepfunctions                                    |
| THUNDRA_AGENT_LAMBDA_AWS_APPSYNC                                       | thundra.agent.lambda.aws.appsync                                          |
| THUNDRA_AGENT_TRACE_INSTRUMENT_DISABLE                                 | thundra.agent.trace.instrument.disable                                    |
| THUNDRA_AGENT_TRACE_INSTRUMENT_TRACEABLECONFIG                         | thundra.agent.trace.instrument.traceableconfig                            |
| THUNDRA_AGENT_TRACE_SPAN_LISTENERCONFIG                                | thundra.agent.trace.span.listenerconfig                                   |
| THUNDRA_AGENT_SAMPLER_TIMEAWARE_TIMEFREQ                               | thundra.agent.sampler.timeaware.timefreq                                  |
| THUNDRA_AGENT_SAMPLER_COUNTAWARE_COUNTFREQ                             | thundra.agent.sampler.countaware.countfreq                                |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SNS_MESSAGE_MASK                  | thundra.agent.trace.integrations.aws.sns.message.mask                     |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SNS_TRACEINJECTION_DISABLE        | thundra.agent.trace.integrations.aws.sns.traceinjection.disable           |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SQS_MESSAGE_MASK                  | thundra.agent.trace.integrations.aws.sqs.message.mask                     |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SQS_TRACEINJECTION_DISABLE        | thundra.agent.trace.integrations.aws.sqs.traceinjection.disable           |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_LAMBDA_PAYLOAD_MASK               | thundra.agent.trace.integrations.aws.lambda.payload.mask                  |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_LAMBDA_TRACEINJECTION_DISABLE     | thundra.agent.trace.integrations.aws.lambda.traceinjection.disable        |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_DYNAMODB_STATEMENT_MASK           | thundra.agent.trace.integrations.aws.dynamodb.statement.mask              |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_DYNAMODB_TRACEINJECTION_ENABLE    | thundra.agent.trace.integrations.aws.dynamodb.traceinjection.enable       |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_ATHENA_STATEMENT_MASK             | thundra.agent.trace.integrations.aws.athena.statement.mask                |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_HTTP_BODY_MASK                        | thundra.agent.trace.integrations.http.body.mask                           |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH                        | thundra.agent.trace.integrations.http.url.depth                           |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_HTTP_TRACEINJECTION_DISABLE           | thundra.agent.trace.integrations.http.traceinjection.disable              |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN            | thundra.agent.trace.integrations.http.error.status.code.min               |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_REDIS_COMMAND_MASK                    | thundra.agent.trace.integrations.redis.command.mask                       |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK                    | thundra.agent.trace.integrations.rdb.statement.mask                       |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_ELASTICSEARCH_BODY_MASK               | thundra.agent.trace.integrations.elasticsearch.body.mask                  |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_ELASTICSEARCH_PATH_DEPTH              | thundra.agent.trace.integrations.elasticsearch.path.depth                 |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_MONGODB_COMMAND_MASK                  | thundra.agent.trace.integrations.mongodb.command.mask                     |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_EVENTBRIDGE_DETAIL_MASK               | thundra.agent.trace.integrations.aws.eventbridge.detail.mask              |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SES_MAIL_MASK                     | thundra.agent.trace.integrations.aws.ses.mail.mask                        |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_SES_MAIL_DESTINATION_MASK         | thundra.agent.trace.integrations.aws.ses.mail.destination.mask            |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_HTTP_DISABLE                          | thundra.agent.trace.integrations.http.disable                             |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_RDB_DISABLE                           | thundra.agent.trace.integrations.rdb.disable                              |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_AWS_DISABLE                           | thundra.agent.trace.integrations.aws.disable                              |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_REDIS_DISABLE                         | thundra.agent.trace.integrations.redis.disable                            |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_ES_DISABLE                            | thundra.agent.trace.integrations.elasticsearch.disable                    |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_MONGO_DISABLE                         | thundra.agent.trace.integrations.mongodb.disable                          |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_SQLALCHEMY_DISABLE                    | thundra.agent.trace.integrations.sqlalchemy.disable                       |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_CHALICE_DISABLE                       | thundra.agent.trace.integrations.chalice.disable                          |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_DJANGO_DISABLE                        | thundra.agent.trace.integrations.django.disable                           |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE                    | thundra.agent.trace.integrations.django.orm.disable                       |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_FLASK_DISABLE                         | thundra.agent.trace.integrations.flask.disable                            |
| THUNDRA_AGENT_TRACE_INTEGRATIONS_FASTAPI_DISABLE                       | thundra.agent.trace.integrations.fastapi.disable                          | 
| THUNDRA_AGENT_LOG_CONSOLE_DISABLE                                      | thundra.agent.log.console.disable                                         |
| THUNDRA_AGENT_LOG_LOGLEVEL                                             | thundra.agent.log.loglevel                                                |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_ENABLE                                   | thundra.agent.lambda.debugger.enable                                      |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_PORT                                     | thundra.agent.lambda.debugger.port                                        |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_LOGS_ENABLE                              | thundra.agent.lambda.debugger.logs.enable                                 |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_WAIT_MAX                                 | thundra.agent.lambda.debugger.wait.max                                    |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_IO_WAIT                                  | thundra.agent.lambda.debugger.io.wait                                     |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_BROKER_PORT                              | thundra.agent.lambda.debugger.broker.port                                 |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_BROKER_HOST                              | thundra.agent.lambda.debugger.broker.host                                 |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_SESSION_NAME                             | thundra.agent.lambda.debugger.session.name                                |
| THUNDRA_AGENT_LAMBDA_DEBUGGER_AUTH_TOKEN                               | thundra.agent.lambda.debugger.auth.token                                  |
| THUNDRA_AGENT_TEST_RUN_ID                 | thundra.agent.test.run.id                                  |
| THUNDRA_AGENT_TEST_PROJECT_ID             | thundra.agent.test.project.id                                  | 
| THUNDRA_AGENT_TEST_STATUS_REPORT_FREQUENCY                               | thundra.agent.test.status.report.freq                                  | 
| THUNDRA_AGENT_TEST_LOG_COUNT_MAX                               | thundra.agent.test.log.count.max                                  || 
THUNDRA_AGENT_TEST_DISABLE                               | thundra.agent.test.disable                                  |
