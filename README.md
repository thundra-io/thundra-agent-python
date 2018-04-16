# Thundra Lambda Agent Python

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

| Name                                     | Type   | Default Value |
|:-----------------------------------------|:------:|:-------------:|
| thundra_apiKey                           | string |       -       |
| thundra_applicationProfile               | string |    default    |
| thundra_disable                          |  bool  |     false     |
| thundra_disable_trace                    |  bool  |     false     |
| thundra_lambda_publish_cloudwatch_enable |  bool  |     false     |
| thundra_lambda_audit_request_skip        |  bool  |     false     |
| thundra_lambda_audit_response_skip       |  bool  |     false     |


#### 2. Object initialization parameters

| Name            | Type   | Default Value |
|:----------------|:------:|:-------------:|
| api_key          | string |       -       |
| disable_trace   |  bool  |     False     |
| request_skip    |  bool  |     False     |
| response_skip   |  bool  |     False     |


## Async Monitoring with Zero Overhead
By default, Thundra agent reports by making an HTTPS request. This adds an overhead to your lambda function.

Instead, you can [setup async monitoring](https://docs.thundra.io/docs/how-to-setup-async-monitoring) in **2 minutes** and monitor your lambda functions with **zero overhead**!
