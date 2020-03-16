import traceback
import hashlib
import base64
import simplejson as json
import copy
import re

from dateutil.parser import parse
from datetime import datetime

from thundra import config
import thundra.constants as constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration
from thundra.application_support import get_application_info
import thundra.utils as utils

from thundra.compat import PY37

OPERATION_TYPE_MAPPING_PATTERNS = utils.get_compiled_operation_type_patterns()

def dummy_func(*args):
    return None


def get_operation_type(class_name, operation_name):
    if class_name in constants.OperationTypeMappings["exclusions"] and \
        operation_name in constants.OperationTypeMappings["exclusions"][class_name]:
        return constants.OperationTypeMappings["exclusions"][class_name][operation_name]
    
    for sre in OPERATION_TYPE_MAPPING_PATTERNS:
        if sre.match(operation_name):
            return constants.OperationTypeMappings["patterns"][sre.pattern]
    return ''


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
        scope.span.domain_name = constants.DomainNames['DB']
        scope.span.class_name = constants.ClassNames['DYNAMODB']

        operation_name, request_data = args
        operation_type = get_operation_type(scope.span.class_name, operation_name)

        self.request_data = request_data.copy()
        self.endpoint = instance._endpoint.host.split('/')[-1]

        tags = {
            constants.SpanTags['OPERATION_TYPE']: operation_type,
            constants.DBTags['DB_INSTANCE']: self.endpoint,
            constants.DBTags['DB_TYPE']: constants.DBTypes['DYNAMODB'],
            constants.AwsDynamoTags['TABLE_NAME']: str(
                self.request_data['TableName']) if 'TableName' in self.request_data else None,
            constants.DBTags['DB_STATEMENT_TYPE']: operation_type,
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
        super(AWSDynamoDBIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

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
            if PY37:
                id_handlers = instance.meta.events._emitter._unique_id_handlers
            else:
                id_handlers = instance.meta.events._unique_id_handlers

            if 'dynamodb-attr-value-input' in id_handlers:
                id_handlers['dynamodb-attr-value-input']['handler'](params=params,
                                                                    model=instance._service_model.operation_model(operation_name))

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
            timestamp = (parse(date_str).replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
        except:
            timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds() - 1

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
            if PY37:
                id_handlers = instance.meta.events._emitter._unique_id_handlers
            else:
                id_handlers = instance.meta.events._unique_id_handlers

            if 'dynamodb-attr-value-input' in id_handlers:
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
            if PY37:
                id_handlers = instance.meta.events._emitter._unique_id_handlers
            else:
                id_handlers = instance.meta.events._unique_id_handlers
            if 'dynamodb-attr-value-input' in id_handlers:
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
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
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
        super(AWSSQSIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)
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

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.request_data = request_data
        self.response = response
        self.message = request_data.get('Message', '')

        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['SNS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
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
        super(AWSSNSIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

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

    def generate_trace_link(self, region, shard_id, sequence_number):
        return region + ':' + self.streamName + ':' + shard_id + ':' + sequence_number

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.streamName = request_data.get('StreamName', '')

        scope.span.domain_name = constants.DomainNames['STREAM']
        scope.span.class_name = constants.ClassNames['KINESIS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
            constants.AwsKinesisTags['STREAM_NAME']: self.streamName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(AWSKinesisIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

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

    def generate_trace_links(self, region, response, data):
        try:
            date_str = response["ResponseMetadata"]["HTTPHeaders"]["date"]
            timestamp = (parse(date_str).replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()

        except:
            timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds() - 1

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
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
            constants.AwsFirehoseTags['STREAM_NAME']: self.deliveryStreamName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(AWSFirehoseIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

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

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.bucket = request_data['Bucket'] if 'Bucket' in request_data else ''

        scope.span.domain_name = constants.DomainNames['STORAGE']
        scope.span.class_name = constants.ClassNames['S3']

        self.objectName = request_data.get('Key', '')

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
            constants.AwsS3Tags['BUCKET_NAME']: self.bucket,
            constants.AwsS3Tags['OBJECT_NAME']: self.objectName
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(AWSS3Integration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

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
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
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

        if not config.lambda_trace_disabled() and 'invoke' in operation_name.lower():
            self.inject_span_context_into_client_context(request_data)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(AWSLambdaIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, response):
        try:
            request_id = response["ResponseMetadata"]["HTTPHeaders"]['x-amzn-requestid']
            return [request_id]
        except Exception:
            return None


class AWSServiceIntegration(BaseIntegration):
    CLASS_TYPE = 'default'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return constants.AWS_SERVICE_REQUEST

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        scope.span.domain_name = constants.DomainNames['AWS']
        scope.span.class_name = constants.ClassNames['AWSSERVICE']

        service_name = instance.__class__.__name__.lower()

        if len(args) > 0:
            scope.span.set_tag(constants.AwsSDKTags['REQUEST_NAME'], args[0])
            scope.span.set_tag(constants.SpanTags['OPERATION_TYPE'], get_operation_type(scope.span.class_name, args[0]))

        scope.span.set_tag(constants.AwsSDKTags['SERVICE_NAME'], service_name)


class AWSAthenaIntegration(BaseIntegration):
    CLASS_TYPE = 'athena'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return self.get_database_name(args) or constants.AWS_SERVICE_REQUEST

    def get_database_name(self, args):
        try:
            database = args[1]['QueryExecutionContext']['Database']
        except:
            database = None
        return database

    def get_output_location(self, args):
        try:
            output_location = args[1]['ResultConfiguration']['OutputLocation']
        except:
            output_location = None
        return output_location

    def get_query(self, args):
        try:
            query = args[1]['QueryString']
        except:
            query = None
        return query

    def get_query_execution_ids(self, args):
        query_execution_ids = None
        if len(args) > 1:
            params = args[1]

            if params and "QueryExecutionId" in params:
                query_execution_ids = [params.get("QueryExecutionId")]
            elif params and "QueryExecutionIds" in params:
                query_execution_ids = params.get("QueryExecutionIds")
        return query_execution_ids

    def get_named_query_ids(self, args):
        named_query_ids = None
        if len(args) > 1:
            params = args[1]

            if params and "NamedQueryId" in params:
                named_query_ids = [params.get("NamedQueryId")]
            elif params and "NamedQueryIds" in params:
                named_query_ids = params.get("NamedQueryIds")
        return named_query_ids

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name = args[0]
        scope.span.domain_name = constants.DomainNames['DB']
        scope.span.class_name = constants.ClassNames['ATHENA']

        tags = {
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
        }

        scope.span.tags = tags

        database = self.get_database_name(args)
        output_location = self.get_output_location(args)
        query_execution_ids = self.get_query_execution_ids(args)
        named_query_ids = self.get_named_query_ids(args)

        if database:
            scope.span.set_tag(constants.SpanTags['DB_INSTANCE'], database)

        if output_location:
            scope.span.set_tag(constants.AthenaTags['S3_OUTPUT_LOCATION'], output_location)

        if not config.athena_statement_masked():
            scope.span.set_tag(constants.DBTags['DB_STATEMENT'], self.get_query(args))

        if query_execution_ids:
            scope.span.set_tag(constants.AthenaTags['REQUEST_QUERY_EXECUTION_IDS'], query_execution_ids)

        if named_query_ids:
            scope.span.set_tag(constants.AthenaTags['REQUEST_NAMED_QUERY_IDS'], named_query_ids)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if response:
            if "QueryExecutionId" in response:
                scope.span.set_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS'],
                                   [response.get("QueryExecutionId")])
            elif "QueryExecutionIds" in response:
                scope.span.set_tag(constants.AthenaTags['RESPONSE_QUERY_EXECUTION_IDS'],
                                   response.get("QueryExecutionIds"))
            elif "NamedQueryId" in response:
                scope.span.set_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS'], [response.get("NamedQueryId")])
            elif "NamedQueryIds" in response:
                scope.span.set_tag(constants.AthenaTags['RESPONSE_NAMED_QUERY_IDS'], response.get("NamedQueryIds"))


class AWSEventBridgeIntegration(BaseIntegration):
    CLASS_TYPE = 'eventbridge'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        operation_name = constants.AwsEventBridgeTags['SERVICE_REQUEST']
        entries = request_data.get('Entries', [])

        if len(entries) == 1:
            operation_name = entries[0]['EventBusName']

        return operation_name

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['EVENTBRIDGE']

        entries = request_data['Entries']
        span_name = self.get_operation_name(wrapped, instance, args, kwargs)

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: get_operation_type(scope.span.class_name, operation_name),
            constants.AwsEventBridgeTags['EVENT_BUS_NAME']: span_name,
            constants.SpanTags['RESOURCE_NAMES']: list(map(lambda x: x.get('DetailType'), entries))
        }

        scope.span.tags = tags

        scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
        scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
        scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
        scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)


    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(AWSEventBridgeIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

        trace_links = self.get_trace_links(response)
        if trace_links:
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], trace_links)

    def get_trace_links(self, response):
        try:
            entries = response['Entries']
            event_ids = []
            for entry in entries:
                if entry.get('EventId'):
                    event_ids.append(entry.get('EventId'))
            return event_ids
        except Exception:
            return None
