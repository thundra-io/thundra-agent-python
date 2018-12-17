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

    def get_operation_name(self):
        return 'dynamodb'

    def getStatementType(self, string):
        if string in Constants.DynamoDBRequestTypes:
            return Constants.DynamoDBRequestTypes[string]
        return 'READ'

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
        self.request_data = request_data
        self.response = response
        self.endpoint = instance._endpoint.host.split('/')[-1]

        scope.span.domain_name = Constants.DomainNames['DB']
        scope.span.class_name = Constants.ClassNames['DYNAMODB']
        scope.span.operation_name = 'dynamodb: ' + str(self.request_data['TableName'])

        ## ADDING TAGS ##

        tags = {
            Constants.SpanTags['SPAN_TYPE']: Constants.SpanTypes['AWS_DYNAMO'],
            Constants.SpanTags['OPERATION_TYPE']: self.getStatementType(operation_name),
            Constants.DBTags['DB_INSTANCE']: self.endpoint,
            Constants.DBTags['DB_TYPE']: Constants.DBTypes['DYNAMODB'],
            Constants.AwsDynamoTags['TABLE_NAME']: str(self.request_data['TableName']),
            Constants.DBTags['DB_STATEMENT_TYPE']: self.getStatementType(operation_name),
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags
        ## FINISHED ADDING TAGS ##
        self.OPERATION.get(operation_name, dummy_func)(scope)

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)

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

    def get_operation_name(self):
        return 'sqs'

    def getRequestType(self, string):
        if string in Constants.SQSRequestTypes:
            return Constants.SQSRequestTypes[string]
        return 'READ'

    def getQueueName(self, data):
        if 'QueueUrl' in data:
            return data['QueueUrl'].split('/')[-1]
        elif 'QueueName' in data:
            return data['QueueName']

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        self.request_data = request_data
        self.queueName = str(self.getQueueName(self.request_data))
        self.response = response

        scope.span.domain_name = Constants.DomainNames['MESSAGING']
        scope.span.class_name = Constants.ClassNames['SQS']
        scope.span.operation_name = self.getRequestType(operation_name)

        ## ADDING TAGS ##

        tags = {
            Constants.SpanTags['SPAN_TYPE']: Constants.SpanTypes['AWS_SQS'],
            Constants.AwsSQSTags['QUEUE_NAME']: self.queueName,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags

        ## FINISHED ADDING TAGS ##

        if exception is not None:
            set_exception(exception, traceback.format_exc(), scope)


class AWSSNSIntegration(BaseIntegration):
    CLASS_TYPE = 'sns'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'sns'

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
        scope.span.operation_name = self.getRequestType(operation_name)

        if operation_name == 'CreateTopic':
            self.topicName = request_data.get('Name', 'N/A')
        else:
            arn = request_data.get(
                        'TopicArn',
                        request_data.get('TargetArn', 'N/A')
                    )
            self.topicName = arn.split(':')[-1]

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


class AWSKinesisIntegration(BaseIntegration):
    CLASS_TYPE = 'kinesis'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'kinesis'

    def getRequestType(self, string):
        if string in Constants.KinesisRequestTypes:
            return Constants.KinesisRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        self.streamName = request_data['StreamName']

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['KINESIS']
        scope.span.operation_name = self.getRequestType(operation_name)


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


class AWSFirehoseIntegration(BaseIntegration):
    CLASS_TYPE = 'firehose'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'firehose'

    def getRequestType(self, string):
        if string in Constants.FirehoseRequestTypes:
            return Constants.FirehoseRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        self.deliveryStreamName = request_data['DeliveryStreamName']

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['FIREHOSE']
        scope.span.operation_name = self.getRequestType(operation_name)

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


class AWSS3Integration(BaseIntegration):
    CLASS_TYPE = 's3'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 's3'

    def getRequestType(self, string):
        if string in Constants.S3RequestTypes:
            return Constants.S3RequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        self.bucket = request_data['Bucket']

        scope.span.domain_name = Constants.DomainNames['STORAGE']
        scope.span.class_name = Constants.ClassNames['S3']
        scope.span.operation_name = self.getRequestType(operation_name)

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


class AWSLambdaIntegration(BaseIntegration):
    CLASS_TYPE = 'lambda'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'lambda'

    def getRequestType(self, string):
        if string in Constants.LambdaRequestType:
            return Constants.LambdaRequestType[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        self.lambdaFunction = request_data.get('FunctionName', '')
        scope.span.domain_name = Constants.DomainNames['API']
        scope.span.class_name = Constants.ClassNames['LAMBDA']
        scope.span.operation_name = self.getRequestType(operation_name)

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsLambdaTags['FUNCTION_NAME']: self.lambdaFunction,
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


class AWSXrayIntegration(BaseIntegration):
    CLASS_TYPE = 'xray'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'xray'

    # def getRequestType(self, string):
    #     if string in Constants.LambdaRequestType:
    #         return Constants.LambdaRequestType[string]
    #     return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):

        operation_name, request_data = args
        # self.lambdaFunction = request_data.get('FunctionName', '')
        # scope.span.domain_name = Constants.DomainNames['API']
        scope.span.class_name = 'XRAY'
        # scope.span.operation_name = 'lambda: ' + self.lambdaFunction

        ### ADDING TAGS ###
        tags = {
            # Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            # Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            # Constants.AwsLambdaTags['FUNCTION_NAME']: self.lambdaFunction,
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
