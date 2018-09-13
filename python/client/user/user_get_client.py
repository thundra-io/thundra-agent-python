import boto3
import json
from random import randint


lambda_client = boto3.client('lambda')
s3 = boto3.client('s3', region_name='us-west-2')


def lambda_handler(event, context):
    payload = {
        'callerId': 'demo',
        'index': randint(0,10)
    }
    try:
        invoke_lambda('python-staging-get-user', payload)
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
