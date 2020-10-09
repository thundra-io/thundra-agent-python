from __future__ import unicode_literals

import base64
import hashlib

import simplejson as json

from thundra import constants, utils
from thundra.compat import str
from thundra.plugins.invocation import invocation_support, invocation_trace_support

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from gzip import GzipFile


class LambdaEventType:
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
    EventBridge = 'eventBridge'


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
            isinstance(original_event.get('resources'), list):
        return LambdaEventType.CloudWatchSchedule

    elif 'awslogs' in original_event and 'data' in original_event['awslogs']:
        return LambdaEventType.CloudWatchLogs

    elif 'deliveryStreamArn' in original_event and isinstance(original_event['records'], list):
        return LambdaEventType.Firehose

    elif 'requestContext' in original_event and 'headers' in original_event:
        return LambdaEventType.APIGatewayProxy

    elif 'context' in original_event and 'params' in original_event and 'header' in original_event['params']:
        return LambdaEventType.APIGateway

    elif 'detail-type' in original_event and 'detail' in original_event and \
            isinstance(original_event.get('resources'), list):
        return LambdaEventType.EventBridge

    elif 'client_context' in vars(original_context):
        return LambdaEventType.Lambda


def inject_trigger_tags_for_kinesis(span, original_event):
    domain_name = constants.DomainNames['STREAM']
    class_name = constants.ClassNames['KINESIS']
    stream_names = []
    trace_links = []
    for record in original_event['Records']:
        event_source_arn = record['eventSourceARN']
        index = event_source_arn.index('/') + 1
        stream_name = event_source_arn[index:]
        stream_names.append(stream_name)

        region = record['awsRegion']
        if "eventID" in record:
            trace_links.append(region + ':' + stream_name + ':' + record["eventID"])
    operation_names = list(set(stream_names))

    invocation_trace_support.add_incoming_trace_links(trace_links)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_firehose(span, original_event):
    domain_name = constants.DomainNames['STREAM']
    class_name = constants.ClassNames['FIREHOSE']
    stream_arn = original_event['deliveryStreamArn']
    index = stream_arn.index('/') + 1
    stream_name = stream_arn[index:]
    operation_names = [stream_name]

    region = original_event['region']

    trace_links = []
    if 'records' in original_event:
        for record in original_event['records']:
            if "approximateArrivalTimestamp" in record and "data" in record:
                timestamp = record["approximateArrivalTimestamp"] / 1000
                try:
                    data = base64.b64decode(record["data"])
                    data_md5 = hashlib.md5(data).hexdigest()

                    trace_links.append(region + ':' + stream_name + ':' + str(int(timestamp - 1)) + ':' + data_md5)
                    trace_links.append(region + ':' + stream_name + ':' + str(int(timestamp)) + ':' + data_md5)
                    trace_links.append(region + ':' + stream_name + ':' + str(int(timestamp + 1)) + ':' + data_md5)

                except Exception:
                    pass

    invocation_trace_support.add_incoming_trace_links(trace_links)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_dynamodb(span, original_event):
    domain_name = constants.DomainNames['DB']
    class_name = constants.ClassNames['DYNAMODB']
    table_names = []
    trace_links = []
    for record in original_event['Records']:
        table_name = record['eventSourceARN'].split('/')[1]
        table_names.append(table_name)

        region = record['awsRegion']

        trace_link_found = False
        if record['eventName'] == "INSERT" or record['eventName'] == "MODIFY":
            new_image = record['dynamodb'].get('NewImage')
            if new_image and new_image.get('x-thundra-span-id'):
                span_id = new_image.get('x-thundra-span-id').get('S')
                trace_link_found = True
                trace_links.append("SAVE:" + span_id)

        elif record['eventName'] == "REMOVE":
            old_image = record['dynamodb'].get('OldImage')
            if old_image and old_image.get('x-thundra-span-id'):
                span_id = old_image.get('x-thundra-span-id').get('S')
                trace_link_found = True
                trace_links.append("DELETE:" + span_id)

        if not trace_link_found:
            creation_time = record['dynamodb'].get('ApproximateCreationDateTime')
            if creation_time:
                if record['eventName'] == "INSERT" or record['eventName'] == "MODIFY":
                    add_dynamodb_trace_links(trace_links, region, table_name, creation_time, "SAVE",
                                             record['dynamodb'].get('NewImage'))
                    add_dynamodb_trace_links(trace_links, region, table_name, creation_time, "SAVE",
                                             record['dynamodb'].get('Keys'))

                elif record['eventName'] == "REMOVE":
                    add_dynamodb_trace_links(trace_links, region, table_name, creation_time, "DELETE",
                                             record['dynamodb'].get('Keys'))

    invocation_trace_support.add_incoming_trace_links(trace_links)

    operation_names = list(set(table_names))
    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def add_dynamodb_trace_links(trace_links, region, table_name, creation_time, operation_type, attributes):
    timestamp = creation_time - 1

    if attributes:
        attributes_hash = hashlib.md5(attributes_to_str(attributes).encode()).hexdigest()

    if attributes_hash:
        for i in range(3):
            trace_links.append(region + ':' + table_name + ':' + str(
                int(timestamp + i)) + ':' + operation_type + ':' + attributes_hash)


def attributes_to_str(attributes):
    sorted_keys = sorted(attributes.keys())
    attributes_sorted = []
    for attr in sorted_keys:
        try:
            key = list(attributes[attr].keys())[0]
            attributes_sorted.append(attr + '=' + '{' + key + ': ' + str(attributes[attr][key]) + '}')
        except Exception:
            pass
    return ', '.join(attributes_sorted)


def inject_trigger_tags_for_sns(span, original_event):
    domain_name = constants.DomainNames['MESSAGING']
    class_name = constants.ClassNames['SNS']
    topic_names = []
    trace_links = []
    for record in original_event['Records']:
        topic_arn = record['Sns']['TopicArn']
        topic_name = topic_arn.split(':')[-1]
        topic_names.append(topic_name)
        if 'MessageId' in record['Sns']:
            trace_links.append(record['Sns']['MessageId'])
    operation_names = list(set(topic_names))

    invocation_trace_support.add_incoming_trace_links(trace_links)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_sqs(span, original_event):
    domain_name = constants.DomainNames['MESSAGING']
    class_name = constants.ClassNames['SQS']
    queue_names = []
    trace_links = []
    for record in original_event['Records']:
        queue_arn = record['eventSourceARN']
        queue_name = queue_arn.split(':')[-1]
        queue_names.append(queue_name)
        trace_links.append(record['messageId'])
    operation_names = list(set(queue_names))

    invocation_trace_support.add_incoming_trace_links(trace_links)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_s3(span, original_event):
    domain_name = constants.DomainNames['STORAGE']
    class_name = constants.ClassNames['S3']
    bucket_names = []
    trace_links = []
    for record in original_event['Records']:
        if "responseElements" in record and "x-amz-request-id" in record["responseElements"]:
            trace_links.append(record["responseElements"]["x-amz-request-id"])
        bucket_names.append(record['s3']['bucket']['name'])
    operation_names = list(set(bucket_names))

    invocation_trace_support.add_incoming_trace_links(trace_links)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_cloudwatch_schedule(span, original_event):
    domain_name = constants.DomainNames['SCHEDULE']
    class_name = constants.ClassNames['SCHEDULE']
    schedule_names = []
    for resource in original_event['resources']:
        schedule_names.append(resource.split('/')[-1])
    operation_names = list(set(schedule_names))

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_cloudwatch_logs(span, original_event):
    domain_name = constants.DomainNames['LOG']
    class_name = constants.ClassNames['CLOUDWATCHLOG']
    operation_names = []
    try:
        compressed_data = base64.b64decode(original_event['awslogs']['data'])
        decompressed_data = json.loads(str(GzipFile(fileobj=BytesIO(compressed_data)).read(), 'utf-8'))
        operation_names = [decompressed_data['logGroup']]
    except Exception as e:
        print('Error handling base64 format!', e)

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_cloudfront(span, original_event):
    domain_name = constants.DomainNames['CDN']
    class_name = constants.ClassNames['CLOUDFRONT']
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
    domain_name = constants.DomainNames['API']
    class_name = constants.ClassNames['APIGATEWAY']

    operation_names = []
    resource = utils.extract_api_gw_resource_name(original_event)
    if resource:
        operation_names.append(resource)
        invocation_support.set_application_resource_name(resource)

    if original_event.get('headers') and 'x-thundra-span-id' in original_event['headers']:
        invocation_trace_support.add_incoming_trace_links([original_event['headers']['x-thundra-span-id']])

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_api_gateway(span, original_event):
    domain_name = constants.DomainNames['API']
    class_name = constants.ClassNames['APIGATEWAY']
    path = '/' + str(original_event['context']['stage']) + str(original_event['params']['path'])
    operation_names = [str(original_event['params']['header']['Host']) + path]

    invocation_support.set_application_resource_name(path)
    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def inject_trigger_tags_for_lambda(span, original_context):
    try:
        if original_context:
            if 'client_context' in vars(original_context):
                if original_context.client_context:
                    if original_context.client_context.custom:
                        domain_name = constants.DomainNames['API']
                        class_name = constants.ClassNames['LAMBDA']
                        operation_names = [original_context.client_context.custom[constants.TRIGGER_OPERATION_NAME_TAG]]

                        inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
                        inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)

        if 'aws_request_id' in vars(original_context):
            invocation_trace_support.add_incoming_trace_links([original_context.aws_request_id])
    except Exception as e:
        pass


def inject_trigger_tags_for_eventbridge(span, original_event):
    domain_name = constants.DomainNames['MESSAGING']
    class_name = constants.ClassNames['EVENTBRIDGE']
    operation_names = [original_event['detail-type']]

    invocation_trace_support.add_incoming_trace_links([original_event['id']])

    inject_trigger_tags_to_span(span, domain_name, class_name, operation_names)
    inject_trigger_tags_to_invocation(domain_name, class_name, operation_names)


def extract_trace_link_from_event(original_event):
    try:
        if '_thundra' in original_event:
            invocation_trace_support.add_incoming_trace_links([original_event['_thundra']['trace_link']])
    except Exception:
        pass


def inject_trigger_tags_to_span(span, domain_name, class_name, operation_names):
    span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], domain_name)
    span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], class_name)
    span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], operation_names)


def inject_trigger_tags_to_invocation(domain_name, class_name, operation_names):
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], domain_name)
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], class_name)
    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], operation_names)
