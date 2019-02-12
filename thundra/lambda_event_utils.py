import base64
import gzip
import json
from enum import Enum
from thundra import constants
from thundra.plugins.invocation import invocation_support



class LambdaEventType(Enum):
    Kinesis = 'kinesis',
    Firehose = 'firehose',
    DynamoDB = 'dynamodb',
    SNS = 'sns',
    SQS = 'sqs',
    S3 = 's3',
    CloudWatchSchedule = 'cloudWatchSchedule',
    CloudWatchLogs = 'cloudWatchLogs',
    CloudFront = 'cloudFront',
    APIGatewayProxy = 'apiGatewayProxy',
    APIGateway = 'apiGateway'
    Lambda = 'lambda'


def get_lambda_event_type(original_event, original_context):
    if 'Records' in original_event:
        if isinstance(original_event['Records'], list):
            records = original_event['Records'][0] or None
            if records is not None:
                if 'dynamodb' in records and records["eventSource"] == "aws:dynamodb":
                    return LambdaEventType.DynamoDB
                if 'kinesis' in records and records['eventSource'] == "aws:kinesis":
                    return LambdaEventType.Kinesis
                if 'EventSource' in records and records['EventSource'] == "aws:sns":
                    return LambdaEventType.SNS
                if 'eventSource' in records and records['eventSource'] == "aws:sqs":
                    return LambdaEventType.SQS
                if 's3' in records:
                    return LambdaEventType.S3
                if 'cf' in records:
                    return LambdaEventType.CloudFront

    elif 'detail-type' in original_event and original_event['detail-type'] == 'Scheduled Event' and \
            isinstance(original_event['resources'], list):
        return LambdaEventType.CloudWatchSchedule

    elif 'awslogs' in original_event and 'data' in original_event['awslogs']:
        return LambdaEventType.CloudWatchLogs

    elif 'deliveryStreamArn' in original_event and isinstance(original_event['records'], list):
        return LambdaEventType.Firehose

    elif 'requestContext' in original_event and 'headers' in original_event:
        return LambdaEventType.APIGatewayProxy

    elif 'context' in original_event and 'params' in original_event and 'header' in original_event['params']:
        return LambdaEventType.APIGateway

    elif 'clientContext' in vars(original_context):
        return LambdaEventType.Lambda

def inject_trigger_tags_for_kinesis(span, original_event):
    domain_name = constants.DomainNames['STREAM']
    class_name = constants.ClassNames['KINESIS']
    stream_names = []
    for record in original_event['Records']:
        event_source_arn = record['eventSourceARN']
        index = event_source_arn.index('/') + 1
        stream_name = event_source_arn[index:]
        stream_names.append(stream_name)
    operation_names = list(set(stream_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_firehose(span, original_event):
    domain_name = constants.DomainNames['STREAM']
    class_name = constants.ClassNames['FIREHOSE']
    stream_arn = original_event['deliveryStreamArn']
    index = stream_arn.index('/') + 1
    stream_name = stream_arn[index:]
    operation_names = [stream_name]

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_dynamodb(span, original_event):
    domain_name = constants.DomainNames['DB']
    class_name = constants.ClassNames['DYNAMODB']
    table_names = []
    for record in original_event['Records']:
        table_names.append(record['eventSourceARN'].split('/')[1])
    operation_names =list(set(table_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_sns(span, original_event):
    domain_name = constants.DomainNames['MESSAGING']
    class_name = constants.ClassNames['SNS']
    topic_names = []
    for record in original_event['Records']:
        topic_arn = record['Sns']['TopicArn']
        topic_name = topic_arn.split(':')[-1]
        topic_names.append(topic_name)
    operation_names = list(set(topic_names))
    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_sqs(span, original_event):
    domain_name = constants.DomainNames['MESSAGING']
    class_name = constants.ClassNames['SQS']
    queue_names = []
    for record in original_event['Records']:
        queue_arn = record['eventSourceARN']
        queue_name = queue_arn.split(':')[-1]
        queue_names.append(queue_name)
    operation_names = list(set(queue_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_s3(span, original_event):
    domain_name = constants.DomainNames['STORAGE']
    class_name = constants.ClassNames['S3']
    bucket_names = []
    for record in original_event['Records']:
        bucket_names.append(record['s3']['bucket']['name'])
    operation_names = list(set(bucket_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_cloudwatch_schedule(span, original_event):
    domain_name = 'Schedule'
    class_name = 'AWS-CloudWatch-Schedule'
    schedule_names = []
    for resource in original_event['resources']:
        schedule_names.append(resource.split('/')[-1])
    operation_names = list(set(schedule_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_cloudwatch_logs(span, original_event):
    domain_name = 'Log'
    class_name = 'AWS-CloudWatch-Log'
    operation_names = []
    try:
        compressed_data = base64.b64decode(original_event['awslogs']['data'])
        decompressed_data = json.loads(str(gzip.decompress(compressed_data), 'utf-8'))
        operation_names = [decompressed_data['logGroup']]
    except:
        print('Error handling base64 format!')
    
    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_cloudfront(span, original_event):
    domain_name = 'CDN'
    class_name = 'AWS-CloudFront'
    uris = []
    for record in original_event['Records']:
        try:
            uris.append(record['cf']['request']['uri'])
        except:
            pass
    operation_names = list(set(uris))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_api_gateway_proxy(span, original_event):
    domain_name = 'API'
    class_name = 'AWS-APIGateway'
    operation_names = [original_event['headers']['Host'] + '/' + original_event['requestContext']['stage'] + \
                        original_event['path']]

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_api_gateway(span, original_event):
    domain_name = 'API'
    class_name = 'AWS-APIGateway'
    operation_names = [str(original_event['params']['header']['Host']) + '/' + str(
        original_event['context']['stage']) + str(original_event['params']['path'])]
    
    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

def inject_trigger_tags_for_lambda(span, original_context):
    if original_context:
        if 'clientContext' in vars(original_context):
            if 'custom' in original_context.clientContext:
                if constants.LAMBDA_TRIGGER_OPERATION_NAME in original_context.clientContext['custom']:
                    domain_name = constants.DomainNames['API']
                    class_name = constants.ClassNames['LAMBDA']
                    operation_names = [original_context.clientContext['custom'][constants.LAMBDA_TRIGGER_OPERATION_NAME]]

                    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
                    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)             

def inject_trigger_tags_to_span(span, domain_name, class_name, operation_names, topology_vertex=True):
    span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], domain_name)
    span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], class_name)
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], topology_vertex)
    span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], operation_names)

def inject_trigger_tags_to_invocation(domain_name, class_name, operation_names):
    invocation_support.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], domain_name)
    invocation_support.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], class_name)
    invocation_support.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], operation_names)