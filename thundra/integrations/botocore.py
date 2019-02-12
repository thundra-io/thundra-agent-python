from __future__ import absolute_import
import traceback
import thundra.constants as constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


def dummy_func(*args):
    return None

def set_exception(exception, traceback_data, scope):
    span = scope.span
    span.set_tag('error.stack', traceback_data)
    span.set_error_to_tag(exception)


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

        self.OPERATION.get(operation_name, dummy_func)(scope)

        if operation_name in constants.DynamoDBRequestTypes:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

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
        if string in constants.SQSRequestTypes:
            return constants.SQSRequestTypes[string]
        return ''

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
        self.response = response

        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['SQS']

        tags = {
            constants.AwsSQSTags['QUEUE_NAME']: self.queueName,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }

        scope.span.tags = tags

        if operation_name in constants.SQSRequestTypes:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

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
        if string in constants.SNSRequestTypes:
            return constants.SNSRequestTypes[string]
        return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.request_data = request_data
        self.response = response

        scope.span.domain_name = constants.DomainNames['MESSAGING']
        scope.span.class_name = constants.ClassNames['SNS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsSNSTags['TOPIC_NAME']: self.topicName
        }

        scope.span.tags = tags

        if operation_name in constants.SNSRequestTypes:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

class AWSKinesisIntegration(BaseIntegration):
    CLASS_TYPE = 'kinesis'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data['StreamName'] if 'StreamName' in request_data else constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        if string in constants.KinesisRequestTypes:
            return constants.KinesisRequestTypes[string]
        return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.streamName = request_data['StreamName'] if 'StreamName' in request_data else ''

        scope.span.domain_name = constants.DomainNames['STREAM']
        scope.span.class_name = constants.ClassNames['KINESIS']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsKinesisTags['STREAM_NAME']: self.streamName
        }

        scope.span.tags = tags

        if 'StreamName' in request_data:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

class AWSFirehoseIntegration(BaseIntegration):
    CLASS_TYPE = 'firehose'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data[
            'DeliveryStreamName'] if 'DeliveryStreamName' in request_data else constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        if string in constants.FirehoseRequestTypes:
            return constants.FirehoseRequestTypes[string]
        return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        operation_name, request_data = args
        self.deliveryStreamName = request_data[
            'DeliveryStreamName'] if 'DeliveryStreamName' in request_data else ''

        scope.span.domain_name = constants.DomainNames['STREAM']
        scope.span.class_name = constants.ClassNames['FIREHOSE']

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsFirehoseTags['STREAM_NAME']: self.deliveryStreamName
        }

        scope.span.tags = tags

        if 'DeliveryStreamName' in request_data:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)


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

        if "Key" in request_data:
            self.objectName = request_data["Key"]

        tags = {
            constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            constants.AwsS3Tags['BUCKET_NAME']: self.bucket,
            constants.AwsS3Tags['OBJECT_NAME']: self.objectName
        }

        scope.span.tags = tags

        if operation_name in constants.S3RequestTypes:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)


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

        if 'Payload' in request_data:
            tags[constants.AwsLambdaTags['INVOCATION_PAYLOAD']] = str(request_data['Payload'],
                                                                      encoding='utf-8') if type(
                request_data['Payload']) is not str else request_data['Payload']

        if 'Qualifier' in request_data:
            tags[constants.AwsLambdaTags['FUNCTION_QUALIFIER']] = request_data['Qualifier']

        if 'InvocationType' in request_data:
            tags[constants.AwsLambdaTags['INVOCATION_TYPE']] = request_data['InvocationType']

        scope.span.tags = tags

        if operation_name in constants.LambdaRequestType:
            scope.span.set_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'], [invocation_support.function_name])
            scope.span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME'], constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(constants.SpanTags['TRIGGER_CLASS_NAME'], constants.LAMBDA_APPLICATION_CLASS_NAME)
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

