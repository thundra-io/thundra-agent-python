from __future__ import absolute_import

import traceback
import time
import thundra.constants as Constants
from thundra.opentracing.tracer import ThundraTracer


# pylint: disable=W0613
def dummy_func(*args):
    return None

class AWSIntegration():
    CLASS_TYPE = 'AWS'
    RESPONSE = {}
    OPERATION = {}

    def __init__(self):
        pass

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        event_operation, _ = args
        scope.span.operation_name = str(event_operation)

        if response is not None:
            self.update_response(response, scope)

    def update_response(self, response, scope):
        try:
            scope.span.status_code = response['ResponseMetadata']['HTTPStatusCode']
            scope.span.transaction_id = response['ResponseMetadata']['RequestId']
        except:
            pass


class AWSDynamoDBIntegration(AWSIntegration):
    CLASS_TYPE = 'dynamodb'

    def __init__(self):
        super(AWSDynamoDBIntegration, self).__init__()
        pass

    def getStatementType(self, string):
        if string in Constants.DynamoDBRequestTypes:
            return Constants.DynamoDBRequestTypes[string]
        return 'READ'

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSDynamoDBIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

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

    def update_response(self, response, scope):
        super(AWSDynamoDBIntegration, self).update_response(response, scope)

    def process_get_item_op(self, scope):
        scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_put_item_op(self, scope):
        if 'Item' in self.request_data:
            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Item'])

    def process_delete_item_op(self, scope):
        scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_update_item_op(self, scope):
        scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], self.request_data['Key'])

    def process_batch_write_op(self, scope):
            table_name = list(self.request_data['RequestItems'].keys())[0]
            items = []
            for item in self.request_data['RequestItems'][table_name]:
                items.append(item)

            scope.span.set_tag(Constants.DBTags['DB_STATEMENT'], items)


class AWSSQSIntegration(AWSIntegration):
    CLASS_TYPE = 'sqs'

    def __init__(self):
        super(AWSSQSIntegration, self).__init__()
        pass

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
        super(AWSSQSIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        operation_name, request_data = args
        self.request_data = request_data
        self.queueName = str(self.getQueueName(self.request_data))
        self.response = response

        scope.span.domain_name = Constants.DomainNames['MESSAGING']
        scope.span.class_name = Constants.ClassNames['SQS']
        scope.span.operation_name = 'sqs: ' + self.queueName

        ## ADDING TAGS ##

        tags = {
            Constants.SpanTags['SPAN_TYPE']: Constants.SpanTypes['AWS_SQS'],
            Constants.AwsSQSTags['QUEUE_NAME']: self.queueName,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
        }
        scope.span.tags = tags

        ## FINISHED ADDING TAGS ##

    def update_response(self, response, scope):
        super(AWSSQSIntegration, self).update_response(response, scope)


class AWSSNSIntegration(AWSIntegration):
    CLASS_TYPE = 'sns'

    def __init__(self):
        super(AWSSNSIntegration, self).__init__()
        pass

    def getRequestType(self, string):
        if string in Constants.SNSRequestTypes:
            return Constants.SNSRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSSNSIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        operation_name, request_data = args
        self.request_data = request_data
        self.response = response

        scope.span.domain_name = Constants.DomainNames['MESSAGING']
        scope.span.class_name = Constants.ClassNames['SNS']
        scope.span.operation_name = 'sns: ' + self.getRequestType(operation_name)

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

    def update_response(self, response, scope):
        super(AWSSNSIntegration, self).update_response(response, scope)


class AWSKinesisIntegration(AWSIntegration):
    CLASS_TYPE = 'kinesis'

    def __init__(self):
        super(AWSKinesisIntegration, self).__init__()
        pass

    def getRequestType(self, string):
        if string in Constants.KinesisRequestTypes:
            return Constants.KinesisRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSKinesisIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )
        operation_name, request_data = args
        self.streamName = request_data['StreamName']

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['KINESIS']
        scope.span.operation_name = 'kinesis: ' + self.streamName


        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsKinesisTags['STREAM_NAME']: self.streamName
        }
        ### FINISHED ADDING TAGS ###
        scope.span.tags = tags

    def update_response(self, response, scope):
        super(AWSKinesisIntegration, self).update_response(response, scope)


class AWSFirehoseIntegration(AWSIntegration):
    CLASS_TYPE = 'firehose'

    def __init__(self):
        super(AWSFirehoseIntegration, self).__init__()
        pass

    def getRequestType(self, string):
        if string in Constants.FirehoseRequestTypes:
            return Constants.FirehoseRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSFirehoseIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        operation_name, request_data = args
        self.deliveryStreamName = request_data['DeliveryStreamName']

        scope.span.domain_name = Constants.DomainNames['STREAM']
        scope.span.class_name = Constants.ClassNames['FIREHOSE']
        scope.span.operation_name = 'firehose: ' + self.deliveryStreamName

        ### ADDING TAGS ###
        tags = {
            Constants.AwsSDKTags['REQUEST_NAME']: operation_name,
            Constants.SpanTags['OPERATION_TYPE']: self.getRequestType(operation_name),
            Constants.AwsFirehoseTags['STREAM_NAME']: self.deliveryStreamName
        }
        ## FINISHED ADDING TAGS ###
        scope.span.tags = tags

    def update_response(self, response, scope):
        super(AWSFirehoseIntegration, self).update_response(response, scope)


class AWSS3Integration(AWSIntegration):
    CLASS_TYPE = 's3'

    def __init__(self):
        super(AWSS3Integration, self).__init__()
        pass

    def getRequestType(self, string):
        if string in Constants.S3RequestTypes:
            return Constants.S3RequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSS3Integration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        operation_name, request_data = args
        self.bucket = request_data['Bucket']

        scope.span.domain_name = Constants.DomainNames['STORAGE']
        scope.span.class_name = Constants.ClassNames['S3']
        scope.span.operation_name = 's3: ' + self.bucket

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

    def update_response(self, response, scope):
        super(AWSS3Integration, self).update_response(response, scope)

class AWSLambdaIntegration(AWSIntegration):
    CLASS_TYPE = 'lambda'

    def __init__(self):
        super(AWSLambdaIntegration, self).__init__()
        pass

    def getRequestType(self, string):
        if string in Constants.LambdaRequestType:
            return Constants.LambdaRequestType[string]
        return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSLambdaIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        operation_name, request_data = args
        self.lambdaFunction = request_data.get('FunctionName', '')
        scope.span.domain_name = Constants.DomainNames['API']
        scope.span.class_name = Constants.ClassNames['LAMBDA']
        scope.span.operation_name = 'lambda: ' + self.lambdaFunction

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

class AWSXrayIntegration(AWSIntegration):
    CLASS_TYPE = 'xray'

    def __init__(self):
        super(AWSXrayIntegration, self).__init__()
        pass

    # def getRequestType(self, string):
    #     if string in Constants.LambdaRequestType:
    #         return Constants.LambdaRequestType[string]
    #     return Constants.AWS_SERVICE_REQUEST

    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        super(AWSXrayIntegration, self).inject_span_info(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

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
            "hi": operation_name
        }
        if 'Payload' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_PAYLOAD']] = request_data['Payload']

        if 'Qualifier' in request_data:
            tags[Constants.AwsLambdaTags['FUNCTION_QUALIFIER']] = request_data['Qualifier']

        if 'InvocationType' in request_data:
            tags[Constants.AwsLambdaTags['INVOCATION_TYPE']] = request_data['InvocationType']
        ## FINISHED ADDING TAGS ###

        scope.span.tags = tags

class AWSIntegrationFactory(object):
    INTEGRATIONS = {
        class_obj.CLASS_TYPE: class_obj
        for class_obj in AWSIntegration.__subclasses__()
    }

    @staticmethod
    def create_span(wrapped, instance, args, kwargs):
        integration_name = instance.__class__.__name__.lower()
        integration_class = AWSIntegrationFactory.INTEGRATIONS.get(
            integration_name,
            None
        )
        
        if integration_class is not None:
            response = None
            exception = None

            tracer = ThundraTracer.get_instance()
            with tracer.start_active_span(operation_name="aws_call", finish_on_close=True) as scope:
                try:
                    response = wrapped(*args, **kwargs)
                    return response
                except Exception as operation_exception:
                    exception = operation_exception
                    scope.span.set_tag('error', exception)
                    raise
                finally:
                    try:
                        integration_class().inject_span_info(
                            scope,
                            wrapped,
                            instance,
                            args,
                            kwargs,
                            response,
                            exception
                        )
                    except Exception as instrumentation_exception:
                        error = {
                            'type': str(type(instrumentation_exception)),
                            'message': str(instrumentation_exception),
                            'traceback': traceback.format_exc(),
                            'time': time.time()
                        }
                        scope.span.set_tag('instrumentation_error', error)

