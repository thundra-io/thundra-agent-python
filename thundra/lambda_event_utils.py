from enum import Enum
from thundra import constants
import base64
import gzip
import json


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


class LambdaEventUtils:
    LAMBDA_TRIGGER_OPERATION_NAME = 'x-thundra-lambda-trigger-operation-name'

    @staticmethod
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

    @staticmethod
    def inject_trigger_tags_for_kinesis(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['STREAM'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['KINESIS'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        stream_names = []
        for record in original_event['Records']:
            event_source_arn = record['eventSourceARN']
            index = event_source_arn.index('/') + 1
            stream_name = event_source_arn[index:]
            stream_names.append(stream_name)
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(stream_names)))

    @staticmethod
    def inject_trigger_tags_for_firehose(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['STREAM'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['FIREHOSE'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        stream_arn = original_event['deliveryStreamArn']
        index = stream_arn.index('/') + 1
        stream_name = stream_arn[index:]
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [stream_name])

    @staticmethod
    def inject_trigger_tags_for_dynamodb(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['DB'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['DYNAMODB'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        table_names = []
        for record in original_event['Records']:
            # event_source_arn = record['eventSourceARN']
            # event_source_arn_split = event_source_arn.split('/')
            # table_name = event_source_arn_split[1]
            # table_names.append(table_name)
            table_names.append(record['eventSourceARN'].split('/')[1])
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(table_names)))

    @staticmethod
    def inject_trigger_tags_for_sns(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['MESSAGING'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['SNS'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        topic_names = []
        for record in original_event['Records']:
            topic_arn = record['Sns']['TopicArn']
            topic_name = topic_arn.split(':')[-1]
            topic_names.append(topic_name)
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(topic_names)))

    @staticmethod
    def inject_trigger_tags_for_sqs(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['MESSAGING'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['SQS'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        queue_names = []
        for record in original_event['Records']:
            queue_arn = record['eventSourceARN']
            queue_name = queue_arn.split(':')[-1]
            queue_names.append(queue_name)
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(queue_names)))

    @staticmethod
    def inject_trigger_tags_for_s3(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['STORAGE'])
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['S3'])
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        bucket_names = []
        for record in original_event['Records']:
            bucket_names.append(record['s3']['bucket']['name'])
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(bucket_names)))

    @staticmethod
    def inject_trigger_tags_for_cloudwatch_schedule(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'Schedule')
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'AWS-CloudWatch-Schedule')
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        schedule_names = []
        for resource in original_event['resources']:
            schedule_names.append(resource.split('/')[-1])
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(schedule_names)))

    @staticmethod
    def inject_trigger_tags_for_cloudwatch_logs(span, original_event):
        try:
            compressed_data = base64.b64decode(original_event['awslogs']['data'])
            decompressed_data = json.loads(str(gzip.decompress(compressed_data), 'utf-8'))
            span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'Log')
            span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'AWS-CloudWatch-Log')
            span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [decompressed_data['logGroup']])
        except:
            print('Error handling base64 format!')

    @staticmethod
    def inject_trigger_tags_for_cloudfront(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'CDN')
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'AWS-CloudFront')
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        uris = []
        for record in original_event['Records']:
            try:
                uris.append(record['cf']['request']['uri'])
            except:
                pass
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], list(set(uris)))

    @staticmethod
    def inject_trigger_tags_for_api_gateway_proxy(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'API')
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'AWS-APIGateway')
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        operation_name = original_event['headers']['Host'] + '/' + original_event['requestContext']['stage'] + \
                         original_event['path']
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [operation_name])

    @staticmethod
    def inject_trigger_tags_for_api_gateway(span, original_event):
        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], 'API')
        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], 'AWS-APIGateway')
        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        operation_name = str(original_event['params']['header']['Host']) + '/' + str(
            original_event['context']['stage']) + str(original_event['params']['path'])
        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [operation_name])

    @staticmethod
    def inject_trigger_tags_for_lambda(span, original_context):
        if original_context:
            if 'clientContext' in vars(original_context):
                if 'custom' in original_context.clientContext:
                    if LambdaEventUtils.LAMBDA_TRIGGER_OPERATION_NAME in original_context.clientContext['custom']:
                        span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.DomainNames['API'])
                        span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.ClassNames['LAMBDA'])
                        span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
                        span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'],
                                     original_context.clientContext['custom'][
                                         LambdaEventUtils.LAMBDA_TRIGGER_OPERATION_NAME])
