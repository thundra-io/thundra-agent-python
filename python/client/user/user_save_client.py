import string

import boto3
import json
import random

lambda_client = boto3.client('lambda')
s3 = boto3.client('s3', region_name='us-west-2')


def lambda_handler(event, context):
    payload = {
        'callerId': 'demo',
        'name': ''.join(random.choices(string.ascii_uppercase, k=5)),
        'surname': ''.join(random.choices(string.ascii_uppercase, k=7)),
        'id': ''.join(random.choices(string.digits, k=15))
    }
    try:
        invoke_lambda('python-staging-save-user', payload)
        #invoke_lambda('python-splunk-get-user', payload)
    except Exception as e:
        print(e)
        raise e


def invoke_lambda(function_name, payload):
    response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload))

    print(response)
