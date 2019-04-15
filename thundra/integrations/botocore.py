import traceback
import hashlib
import base64
import json
import copy

from dateutil.parser import parse
from datetime import datetime

from thundra import config
import thundra.constants as constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration
from thundra.application_support import get_application_info


def dummy_func(*args):
    return None


class AWSDynamoDBIntegration(BaseIntegration):
    CLASS_TYPE = 'dynamodb'

    def __init__(self):
        self.OPERATION = {
            'PutItem': self.process_put_item_op,
            'UpdateItem': self.process_update_item_op,
            'GetItem': self.process_get_item_op,
            'DeleteItem': self.process_delete_item_op,
            'BatchWriteItem': self.process_batch_write_op,
        }

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return str(request_data['TableName']) if 'TableName' in request_data else constants.AWS_SERVICE_REQUEST

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        statement_type = constants.DynamoDBRequestTypes.get(operation_name, '')

        self.request_data = request_data.copy()
        self.endpoint = instance._endpoint.host.split('/')[-1]

        scope.span.domain_name = constants.DomainNames['DB']
        scope.span.class_name = constants.ClassNames['DYNAMODB']

        tags = {
            constants.SpanTags['OPERATION_TYPE']: statement_type,
            constants.DBTags['DB_INSTANCE']: self.endpoint,
            constants.DBTags['DB_TYPE']: constants.DBTypes['DYNAMODB'],
            constants.AwsDynamoTags['TABLE_NAME']: str(
                self.request_data['TableName']) if 'TableName' in self.request_data else None,
            constants.DBTags['DB_STATEMENT_TYPE']: statement_type,
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags

        # Check if Key and Item fields have any byte field and convert to string
        if 'Key' in self.request_data:
            self.escape_byte_fields(self.request_data['Key'])
        if 'Item' in self.request_data:
            self.escape_byte_fields(self.request_data['Item'])

        # DB statement tags should not be set on span if masked
        if not config.dynamodb_statement_masked():
            self.OPERATION.get(operation_name, dummy_func)(scope)

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

        if config.dynamodb_trace_enabled():
            if operation_name == 'PutItem':
                self.inject_trace_link_on_put(scope.span, request_data, instance)

            if operation_name == 'UpdateItem':
                self.inject_trace_link_on_update(scope.span, request_data, instance)

            if operation_name == 'DeleteItem':
                self.inject_trace_link_on_delete(request_data)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        if scope.span.get_tag(constants.SpanTags['TRACE_LINKS']):
            return

        trace_links = self.get_trace_links(instance, args, response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, instance, args, response):
        operation_name, request_data = args
        trace_links = None

        try:
            params = copy.deepcopy(request_data)
            if 'dynamodb-attr-value-input' in instance.meta.events._unique_id_handlers:
                instance.meta.events._unique_id_handlers['dynamodb-attr-value-input']['handler'](params=params,
                                                                                                 model=instance._service_model.operation_model(
                                                                                                     operation_name))
            region = instance.meta.region_name

            if operation_name == 'PutItem':
                trace_links = self.generate_trace_links(region, response, params['TableName'], 'SAVE',
                                                        params['Item'])

            elif operation_name == 'UpdateItem':
                trace_links = self.generate_trace_links(region, response, params['TableName'], 'SAVE',
                                                        params['Key'])

            elif operation_name == 'DeleteItem':
                if config.dynamodb_trace_enabled() and 'Attributes' in response:
                    span_id = response['Attributes'].get("x-thundra-span-id")
                    if span_id and span_id.get('S'):
                        trace_links = ['DELETE:' + span_id.get('S')]

                if not trace_links:
                    trace_links = self.generate_trace_links(region, response, params['TableName'], 'DELETE',
                                                            params['Key'])

        except Exception as e:
            pass

        return trace_links

    def generate_trace_links(self, region, response, table_name, operation_type, attributes):
        try:
            date_str = response["ResponseMetadata"]["HTTPHeaders"]["date"]
            timestamp = parse(date_str).timestamp()
        except:
            timestamp = datetime.now().timestamp() - 1

        attributes_hash = hashlib.md5(self.attributes_to_str(attributes).encode()).hexdigest()

        trace_links = [
            region + ':' + table_name + ':' + str(int(timestamp + i)) + ':' + operation_type + ':' + attributes_hash for
            i in range(3)]
        return trace_links

    @staticmethod
    def attributes_to_str(attributes):
        sorted_keys = sorted(attributes.keys())
        attributes_sorted = []
        for attr in sorted_keys:
            try:
                key = list(attributes[attr].keys())[0]
                attributes_sorted.append(attr + '=' + '{' + key + ': ' + str(attributes[attr][key]) + '}')
            except Exception as e:
                pass
        return ', '.join(attributes_sorted)

    def inject_trace_link_on_put(self, span, request_data, instance):

        thundra_span = {'S': span.span_id}
        try:
            if 'dynamodb-attr-value-input' in instance.meta.events._unique_id_handlers:
                thundra_span = span.span_id
        except Exception as e:
            pass

        try:
            if 'Item' in request_data:
                request_data['Item']['x-thundra-span-id'] = thundra_span
            else:
                request_data['Item'] = {'x-thundra-span-id': thundra_span}

            span.set_tag(constants.SpanTags['TRACE_LINKS'], ["SAVE:" + span.span_id])
        except:
            pass

    def inject_trace_link_on_update(self, span, request_data, instance):

        thundra_span = {'S': span.span_id}
        try:
            if 'dynamodb-attr-value-input' in instance.meta.events._unique_id_handlers:
                thundra_span = span.span_id
        except Exception as e:
            pass

        thundra_attr = {'Action': 'PUT', 'Value': thundra_span}

        try:
            if 'AttributeUpdates' in request_data:
                request_data['AttributeUpdates']['x-thundra-span-id'] = thundra_attr
            else:
                request_data['AttributeUpdates'] = {'x-thundra-span-id': thundra_attr}

            span.set_tag(constants.SpanTags['TRACE_LINKS'], ["SAVE:" + span.span_id])
        except:
            pass

    def inject_trace_link_on_delete(self, request_data):
        try:
            request_data['ReturnValues'] = "ALL_OLD"
        except:
            pass

    def process_get_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_put_item_op(self, scope):
        if 'Item' in self.request_data:
            scope.span.set_tag(constants.DBTags['DB_STATEMENT'], self.request_data['Item'])

    def process_delete_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_update_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def escape_byte_fields(self, req_dict):
        for k, v in req_dict.items():
            if type(v) == dict:
                for f, fv in v.items():
                    if type(fv) == bytes:
                        v[f] = fv.decode()
                    elif type(fv) == list and len(fv) != 0 and type(fv[0]) == bytes:
                        v[f] = [e.decode() for e in fv]
            elif type(v) == bytes:
                req_dict[k] = v.decode()
            elif type(v) == list and len(v) != 0 and type(v[0]) == bytes:
                req_dict[k] = [e.decode() for e in v]

    def process_batch_write_op(self, scope):
        table_name = list(self.request_data['RequestItems'].keys())[0]
        items = []
        for item in self.request_data['RequestItems'][table_name]:
            items.append(item)

        scope.span.set_tag(constants.DBTags['DB_STATEMENT'], items)


class AWSSQSIntegration(BaseIntegration):
    CLASS_TYPE = 'sqs'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        queue_name = str(self.getQueueName(request_data))
        if queue_name != '':
            return queue_name
        return constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        return constants.SQSRequestTypes.get(string, '')

    def getQueueName(self, data):
        if 'QueueUrl' in data:
            return data['QueueUrl'].split('/')[-1]
        elif 'QueueName' in data:
            return data['QueueName']
        return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.request_data = request_data
        self.queueName = str(self.getQueueName(self.request_data))

        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['SQS']

        tags = {
            constants.AwsSQSTags['QUEUE_NAME']: self.queueName,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

        if not config.sqs_message_masked():
            if operation_name == "SendMessage":
                message = request_data.get("MessageBody", "")
                scope.span.set_tag(constants.AwsSQSTags['MESSAGE'], message)

            elif operation_name == "SendMessageBatch":
                entries = request_data.get('Entries', None)
                messages = []
                if entries:
                    for entry in entries:
                        messages.append(entry.get("MessageBody", ""))
                scope.span.set_tag(constants.AwsSQSTags['MESSAGES'], messages)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)
        operation_name = args[0]

        trace_links = self.get_trace_links(operation_name, response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    @staticmethod
    def get_trace_links(operation_name, response):
        if operation_name == 'SendMessage':
            message_id = response['MessageId']
            return [message_id]

        elif operation_name == 'SendMessageBatch':
            if len(response['Successful']) > 0:
                links = []
                entries = response['Successful']
                for entry in entries:
                    links.append(entry['MessageId'])
                return links
        return None


class AWSSNSIntegration(BaseIntegration):
    CLASS_TYPE = 'sns'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        operation_name, request_data = args
        if operation_name == 'CreateTopic':
            self.topicName = request_data.get('Name', 'N/A')
        else:
            arn = request_data.get(
                'TopicArn',
                request_data.get('TargetArn', 'N/A')
            )
            if arn != 'N/A':
                self.topicName = arn.split(':')[-1]
            else:
                self.topicName = ''

        return self.topicName

    def getRequestType(self, string):
        return constants.SNSRequestTypes.get(string, '')

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.request_data = request_data
        self.response = response
        self.message = request_data.get('Message', '')

        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['SNS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsSNSTags['TOPIC_NAME']: self.topicName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

        if not config.sns_message_masked():
            scope.span.set_tag(constants.AwsSNSTags['MESSAGE'], self.message)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    @staticmethod
    def get_trace_links(response):
        try:
            message_id = response['MessageId']
            return [message_id]
        except Exception:
            return None


class AWSKinesisIntegration(BaseIntegration):
    CLASS_TYPE = 'kinesis'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data.get('StreamName', constants.AWS_SERVICE_REQUEST)

    def getRequestType(self, string):
        return constants.KinesisRequestTypes.get(string, '')

    def generate_trace_link(self, region, shard_id, sequence_number):
        return region + ':' + self.streamName + ':' + shard_id + ':' + sequence_number

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.streamName = request_data.get('StreamName', '')

        scope.span.domain_name = constants.DomainNames['STREAM']
        scope.span.class_name = constants.ClassNames['KINESIS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsKinesisTags['STREAM_NAME']: self.streamName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(instance.meta.region_name, response)
        scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, region, response):
        trace_links = []
        try:
            if "Records" in response:
                records = response["Records"]
                for record in records:
                    trace_links.append(
                        self.generate_trace_link(region, record["ShardId"], record["SequenceNumber"]))
            else:
                trace_links.append(
                    self.generate_trace_link(region, response["ShardId"], response["SequenceNumber"]))
        except:
            return None

        return trace_links


class AWSFirehoseIntegration(BaseIntegration):
    CLASS_TYPE = 'firehose'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data.get('DeliveryStreamName', constants.AWS_SERVICE_REQUEST)

    def getRequestType(self, string):
        return constants.FirehoseRequestTypes.get(string, '')

    def generate_trace_links(self, region, response, data):
        try:
            date_str = response["ResponseMetadata"]["HTTPHeaders"]["date"]
            timestamp = parse(date_str).timestamp()
        except:
            timestamp = datetime.now().timestamp() - 1

        if isinstance(data, str):
            data = data.encode()
        data_md5 = hashlib.md5(data).hexdigest()

        trace_links = [region + ':' + self.deliveryStreamName + ':' + str(int(timestamp + i)) + ':' + data_md5 for i in
                       range(3)]
        return trace_links

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.deliveryStreamName = request_data.get('DeliveryStreamName', '')

        scope.span.domain_name = constants.DomainNames['STREAM']
        scope.span.class_name = constants.ClassNames['FIREHOSE']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsFirehoseTags['STREAM_NAME']: self.deliveryStreamName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(args, instance.meta.region_name, response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, args, region, response):
        trace_links = []
        try:
            operation_name, request_data = args

            if operation_name == "PutRecord":
                data = request_data["Record"]["Data"]
                trace_links = self.generate_trace_links(region, response, data)

            elif operation_name == "PutRecordBatch":
                for record in request_data["Records"]:
                    links = self.generate_trace_links(region, response, record["Data"])
                    trace_links.extend(links)

        except Exception as e:
            pass

        return trace_links if len(trace_links) > 0 else None


class AWSS3Integration(BaseIntegration):
    CLASS_TYPE = 's3'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data['Bucket'] if 'Bucket' in request_data else constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        if string in constants.S3RequestTypes:
            return constants.S3RequestTypes[string]
        return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.bucket = request_data['Bucket'] if 'Bucket' in request_data else ''

        scope.span.domain_name = constants.DomainNames['STORAGE']
        scope.span.class_name = constants.ClassNames['S3']

        self.objectName = request_data.get('Key', '')

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsS3Tags['BUCKET_NAME']: self.bucket,
            constants.AwsS3Tags['OBJECT_NAME']: self.objectName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, response):
        try:
            request_id = response["ResponseMetadata"]["HTTPHeaders"]['x-amz-request-id']
            return [request_id]
        except Exception:
            return None


class AWSLambdaIntegration(BaseIntegration):
    CLASS_TYPE = 'lambda'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data.get('FunctionName', constants.AWS_SERVICE_REQUEST)

    def getRequestType(self, string):
        if string in constants.LambdaRequestType:
            return constants.LambdaRequestType[string]
        return ''

    def inject_span_context_into_client_context(self, request_data):
        encoded_client_context = request_data.get('X-Amz-Client-Context', None)
        client_context = {}
        if encoded_client_context != None:
            client_context = json.loads(base64.b64decode(encoded_client_context))

        custom = {}
        if 'custom' in client_context:
            custom = client_context['custom']

        application_info = get_application_info()

        custom[constants.TRIGGER_DOMAIN_NAME_TAG] = application_info['applicationDomainName']
        custom[constants.TRIGGER_CLASS_NAME_TAG] = application_info['applicationClassName']
        custom[constants.TRIGGER_OPERATION_NAME_TAG] = application_info['applicationName']

        client_context['custom'] = custom
        encoded_client_context = base64.b64encode(json.dumps(client_context).encode()).decode()
        request_data['ClientContext'] = encoded_client_context

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.lambdaFunction = request_data.get('FunctionName', '')
        scope.span.domain_name = constants.DomainNames['API']
        scope.span.class_name = constants.ClassNames['LAMBDA']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsLambdaTags['FUNCTION_NAME']: self.lambdaFunction,
        }

        if not config.lambda_payload_masked() and 'Payload' in request_data:
            tags[constants.AwsLambdaTags['INVOCATION_PAYLOAD']] = str(request_data['Payload'],
                                                                      encoding='utf-8') if type(
                request_data['Payload']) is not str else request_data['Payload']

        if 'Qualifier' in request_data:
            tags[constants.AwsLambdaTags['FUNCTION_QUALIFIER']] = request_data['Qualifier']

        if 'InvocationType' in request_data:
            tags[constants.AwsLambdaTags['INVOCATION_TYPE']] = request_data['InvocationType']

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

        if not config.lambda_trace_disabled():
            self.inject_span_context_into_client_context(request_data)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, response):
        try:
            request_id = response["ResponseMetadata"]["HTTPHeaders"]['x-amzn-requestid']
            return [request_id]
        except Exception:
            return None
