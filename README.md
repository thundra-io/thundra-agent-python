# Thundra Lambda Agent Python 
[![CircleCI](https://circleci.com/gh/thundra-io/thundra-lambda-agent-python.svg?style=svg)](https://circleci.com/gh/thundra-io/thundra-lambda-agent-python)
[![PyPI](https://img.shields.io/pypi/v/nine.svg)](https://pypi.org/project/thundra/)


Trace your AWS lambda functions with async monitoring by [Thundra](https://www.thundra.io//)!

## Installation

Run this command from your project directory:
```bash
pip3 install thundra -t .
```
## Usage

Just import this module, pass your api key to it and use our decorator to wrap your handler:
```python
from thundra.thundra_agent import Thundra

thundra = Thundra(api_key=<your api key is here>)

@thundra
def handler(event, context):
    print("Hello Thundra!")
```

## Configuration
You can configure Thundra using **environment variables** or **module initialization parameters**.

Environment variables have **higher precedence** over initialization parameters.

Check out the [configuration part](https://docs.thundra.io/docs/python-configuration) of our docs for more detailed information.

#### 1. Environment variables

| Name                                          | Type   |          Default Value           |
|:----------------------------------------------|:------:|:--------------------------------:|
| thundra_apiKey                                | string |                -                 |
| thundra_agent_lambda_disable                  |  bool  |              false               |
| thundra_agent_lambda_application_stage        | string |                -                 |
| thundra_agent_lambda_trace_disable            |  bool  |              false               |
| thundra_agent_lambda_metric_disable           |  bool  |              false               |
| thundra_agent_lambda_log_disable              |  bool  |              false               |
| thundra_agent_lambda_trace_request_skip       |  bool  |              false               |
| thundra_agent_lambda_trace_response_skip      |  bool  |              false               |
| thundra_agent_lambda_timeout_margin           |  int   |               200                |
| thundra_agent_lambda_report_rest_baseUrl      | string |     https://api.thundra.io/v1    |
| thundra_agent_lambda_report_cloudwatch_enable |  bool  |              false               |



#### 2. Object initialization parameters

| Name            | Type   | Default Value |
|:----------------|:------:|:-------------:|
| api_key         | string |       -       |
| disable_trace   |  bool  |     False     |
| disable_metric  |  bool  |     False     |
| disable_log     |  bool  |     False     |


## Async Monitoring with Zero Overhead
By default, Thundra agent reports by making an HTTPS request. This adds an overhead to your lambda function.

Instead, you can [setup async monitoring](https://docs.thundra.io/docs/how-to-setup-async-monitoring) in **2 minutes** and monitor your lambda functions with **zero overhead**!

## Log Plugin
Log plugin is added by default, but in order to enable it, you should add `ThundraLogHandler` to your logger.

You can either add it via logging.conf or add during getting logger object.

#### Configurepy tes via logging.conf
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
