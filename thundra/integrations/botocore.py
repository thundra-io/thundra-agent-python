from __future__ import absolute_import
import thundra.constants as Constants
from thundra.integrations.base_integration import BaseIntegration
import traceback


# pylint: disable=W0613


def dummy_func(*args):
    return None


def set_exception(exception, traceback_data, scope):
    span = scope.span
    span.set_tag('error.stack', traceback_data)
    span.set_error_to_tag(exception)


class AWSDynamoDBIntegration(BaseIntegration):
    CLASS_TYPE = 'dynamodb'
    OPERATION = {}

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return str(request_data['TableName']) if 'TableName' in request_data else Constants.AWS_SERVICE_REQUEST

    def getStatementType(self, string):
        if string in Constants.DynamoDBRequestTypes:
            return Constants.DynamoDBRequestTypes[string]
        return ''

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        self.OPERATION.update(
            {'PutItem': self.process_put_item_op,
             'UpdateItem': self.process_update_item_op,
             'GetItem': self.process_get_item_op,
             'DeleteItem': self.process_delete_item_op,
             'BatchWriteItem': self.process_batch_write_op,
             }
        )

        operation_name, request_data = args
        self.request_data = request_data.copy()
        self.response = response
        self.endpoint = instance._endpoint.host.split('/')[-1]

        scope.span.domain_name = Constants.DomainNames['DB']
        scope.span.class_name = Constants.ClassNames['DYNAMODB']

        ## ADDING TAGS ##

        tags = {
            Constants.SpanTags['OPERATION_TYPE']: self.getStatementType(operation_name),
            Constants.DBTags['DB_INSTANCE']: self.endpoint,
            Constants.DBTags['DB_TYPE']: Constants.DBTypes['DYNAMODB'],
            Constants.AwsDynamoTags['TABLE_NAME']: str(
                self.request_data['TableName']) if 'TableName' in self.request_data else None,
            Constants.DBTags['DB_STATEMENT_TYPE']: self.getStatementType(operation_name),
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags
        ## FINISHED ADDING TAGS ##

        # Check if Key and Item fields have any byte field and convert to string
        if 'Key' in self.request_data:
            self.escape_byte_fields(self.request_data['Key'])
        if 'Item' in self.request_data:
            self.escape_byte_fields(self.request_data['Item'])


        self.OPERATION.get(operation_name, dummy_func)(scope)

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if operation_name in Constants.DynamoDBRequestTypes:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)

    def process_get_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_put_item_op(self, scope):
        if 'Item' in self.request_data:
            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Item'])

    def process_delete_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_update_item_op(self, scope):
        if 'Key' in self.request_data:
            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

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

        scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], items)


class AWSSQSIntegration(BaseIntegration):
    CLASS_TYPE = 'sqs'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return str(self.getQueueName(request_data))

    def getRequestType(self, string):
        if string in Constants.SQSRequestTypes:
            return Constants.SQSRequestTypes[string]
        return 'READ'

    def getQueueName(self, data):
        if 'QueueUrl' in data:
            return data['QueueUrl'].split('/')[-1]
        elif 'QueueName' in data:
            return data['QueueName']
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.request_data = request_data
        self.queueName = str(self.getQueueName(self.request_data))
        self.response = response

        scope.span.domain_name = Constants.DomainNames['MESSAGING']
        scope.span.class_name = Constants.ClassNames['SQS']

        ## ADDING TAGS ##

        tags = {
            Constants.AwsSQSTags['QUEUE_NAME']: self.queueName,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags

        ## FINISHED ADDING TAGS ##

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if operation_name in Constants.SQSRequestTypes:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


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
                self.topicName = Constants.AWS_SERVICE_REQUEST

        return self.topicName

    def getRequestType(self, string):
        if string in Constants.SNSRequestTypes:
            return Constants.SNSRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.request_data = request_data
        self.response = response

        scope.span.domain_name = Constants.DomainNames['MESSAGING']
        scope.span.class_name = Constants.ClassNames['SNS']

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsSNSTags['TOPIC_NAME']: self.topicName
        }
        ### FINISHED ADDING TAGS ###
        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if operation_name in Constants.SNSRequestTypes:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


class AWSKinesisIntegration(BaseIntegration):
    CLASS_TYPE = 'kinesis'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data['StreamName'] if 'StreamName' in request_data else Constants.AWS_SERVICE_REQUEST
        # return 'kinesis'

    def getRequestType(self, string):
        if string in Constants.KinesisRequestTypes:
            return Constants.KinesisRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.streamName = request_data['StreamName'] if 'StreamName' in request_data else Constants.AWS_SERVICE_REQUEST

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['KINESIS']

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsKinesisTags['STREAM_NAME']: self.streamName
        }
        ### FINISHED ADDING TAGS ###
        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if 'StreamName' in request_data:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


class AWSFirehoseIntegration(BaseIntegration):
    CLASS_TYPE = 'firehose'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data[
            'DeliveryStreamName'] if 'DeliveryStreamName' in request_data else Constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        if string in Constants.FirehoseRequestTypes:
            return Constants.FirehoseRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.deliveryStreamName = request_data[
            'DeliveryStreamName'] if 'DeliveryStreamName' in request_data else Constants.AWS_SERVICE_REQUEST

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['FIREHOSE']

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsFirehoseTags['STREAM_NAME']: self.deliveryStreamName
        }
        ## FINISHED ADDING TAGS ###
        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if 'DeliveryStreamName' in request_data:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


class AWSS3Integration(BaseIntegration):
    CLASS_TYPE = 's3'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data['Bucket'] if 'Bucket' in request_data else Constants.AWS_SERVICE_REQUEST

    def getRequestType(self, string):
        if string in Constants.S3RequestTypes:
            return Constants.S3RequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.bucket = request_data['Bucket'] if 'Bucket' in request_data else Constants.AWS_SERVICE_REQUEST

        scope.span.domain_name = Constants.DomainNames['STORAGE']
        scope.span.class_name = Constants.ClassNames['S3']

        if "Key" in request_data:
            self.objectName = request_data["Key"]

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsS3Tags['BUCKET_NAME']: self.bucket,
            Constants.AwsS3Tags['OBJECT_NAME']: self.objectName
        }
        ## FINISHED ADDING TAGS ###
        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if operation_name in Constants.S3RequestTypes:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


class AWSLambdaIntegration(BaseIntegration):
    CLASS_TYPE = 'lambda'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        _, request_data = args
        return request_data.get('FunctionName', Constants.AWS_SERVICE_REQUEST)

    def getRequestType(self, string):
        if string in Constants.LambdaRequestType:
            return Constants.LambdaRequestType[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        self.lambdaFunction = request_data.get('FunctionName', Constants.AWS_SERVICE_REQUEST)
        scope.span.domain_name = Constants.DomainNames['API']
        scope.span.class_name = Constants.ClassNames['LAMBDA']

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsLambdaTags['FUNCTION_NAME']: self.lambdaFunction,
        }
        if 'Payload' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_PAYLOAD']] = str(request_data['Payload'],
                                                                      encoding='utf-8') if type(
                request_data['Payload']) is not str else request_data['Payload']

        if 'Qualifier' in request_data:
            tags[Constants.AwsLambdaTags['FUNCTION_QUALIFIER']] = request_data['Qualifier']

        if 'InvocationType' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_TYPE']] = request_data['InvocationType']
        ## FINISHED ADDING TAGS ###

        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

        if operation_name in Constants.LambdaRequestType:
            scope.span.set_tag(Constants.SpanTags['TRIGGER_OPERATION_NAMES'], [scope.span.tracer.function_name])
            scope.span.set_tag(Constants.SpanTags['TOPOLOGY_VERTEX'], True)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_DOMAIN_NAME'], Constants.LAMBDA_APPLICATION_DOMAIN_NAME)
            scope.span.set_tag(Constants.SpanTags['TRIGGER_CLASS_NAME'], Constants.LAMBDA_APPLICATION_CLASS_NAME)


class AWSXrayIntegration(BaseIntegration):
    CLASS_TYPE = 'xray'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return 'xray'

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                         exception):

        operation_name, request_data = args
        scope.span.class_name = 'XRAY'

        ### ADDING TAGS ###
        tags = {
            "XRAY": 'Under_Development'
        }
        if 'Payload' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_PAYLOAD']] = request_data['Payload']

        if 'Qualifier' in request_data:
            tags[Constants.AwsLambdaTags['FUNCTION_QUALIFIER']] = request_data['Qualifier']

        if 'InvocationType' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_TYPE']] = request_data['InvocationType']
        ## FINISHED ADDING TAGS ###

        scope.span.tags = tags

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)
