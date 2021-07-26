# Thundra Agent Python For Tracing

[![OpenTracing Badge](https://img.shields.io/badge/OpenTracing-enabled-blue.svg)](http://opentracing.io)
[![Pyversions](https://img.shields.io/pypi/pyversions/thundra.svg?style=flat)](https://pypi.org/project/thundra/)
[![PyPI](https://img.shields.io/pypi/v/thundra.svg)](https://pypi.org/project/thundra/)

Trace your marvelous python projects with async monitoring by [Thundra](https://start.thundra.me/)!

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
- [Getting Help](#getting-help)
- [Opening Issues](#opening-issues)


## Installation

Run this command from your project directory:
```bash
pip install thundra -t .
```

## Configuration
You can configure Thundra using **environment variables** or **module initialization parameters**.

Environment variables have **higher precedence** over initialization parameters.

Check out the [configuration part](https://docs.thundra.io/python/configuration-options) of our docs for more detailed information.

#### 1. Environment variables

| Name                                          | Type   |          Default Value           |
|:----------------------------------------------|:------:|:--------------------------------:|
| THUNDRA_APIKEY                                | string |                -                 |
| THUNDRA_APPLICATION_NAME                      | string |                -                 |
| THUNDRA_APPLICATION_STAGE                     | string |                -                 |
| THUNDRA_TRACE_DISABLE                         |  bool  |              false               |
| THUNDRA_METRIC_DISABLE                        |  bool  |              false               |
| THUNDRA_LOG_DISABLE                           |  bool  |              false               |
| THUNDRA_TRACE_REQUEST_SKIP                    |  bool  |              false               |
| THUNDRA_TRACE_RESPONSE_SKIP                   |  bool  |              false               |
| THUNDRA_LAMBDA_TIMEOUT_MARGIN                 |  int   |               200                |
| THUNDRA_REPORT_REST_BASEURL                   | string |     https://api.thundra.io/v1    |
| THUNDRA_REPORT_CLOUDWATCH_ENABLE              |  bool  |              false               |


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
export THUNDRA_APIKEY =<your_thundra_api_key>
export THUNDRA_APPLICATION_NAME=<app-name>
<python command>
```

For illustration of Fastapi:
```sh
export THUNDRA_APIKEY =<your_thundra_api_key>
export THUNDRA_APPLICATION_NAME=fastapi-prod
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
export THUNDRA_APIKEY =<your_thundra_api_key>
export THUNDRA_APPLICATION_NAME=<your_application_name>
```

```python
import thundra

@thundra.<framework_wrapper>
def handler(event, context):
    print("Hello Thundra!")
```

To run on your framework please refer to [supported frameworks](#frameworks)

###  Request Body

Normally thundra does not get your project's requests' body. In order to see request body on tracing data, following environment variable shall be set besides api key and application name:

```sh
export THUNDRA_TRACE_REQUEST_SKIP=True
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

### AWS Lambda

Tracing Lambda functions:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)

**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method, just change `@thundra.<framework_wrapper>` by `@thundra.lambda_wrapper`.

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
                "thundra.agent.trace.integrations.django.orm.disable": True,
                "thundra.agent.trace.integrations.rdb.disable": True
            }
        }
    )
    ```


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method, just change `@thundra.<framework_wrapper>` by `@thundra.django_wrapper`.


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
- For decorator tracing method, just change `@thundra.<framework_wrapper>` by `@thundra.flask_wrapper`.

### Fastapi

Tracing Fastapi application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method, just change `@thundra.<framework_wrapper>` by `@thundra.fastapi_wrapper`.
- Fastapi has been supported for python 3.7 and above.

### Chalice

Tracing Fastapi application:

1. Auto trace by using one of the following methods:
    - [No-Code Change Tracing](#no-code-change-tracing).
    - [In-Code Configuration Tracing](#in-code-configuration-tracing)
2. Trace specific endpoints by [Decorator](#decorator)


**NOTES**

- Make sure to choose just one of the methods.
- For decorator tracing method, just change `@thundra.<framework_wrapper>` by `@thundra.fastapi_wrapper`.


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

#### Configurepy test via logging.conf
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