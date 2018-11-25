from __future__ import absolute_import

import traceback

import thundra.constants as Constants


# pylint: disable=W0613
def dummy_func(*args):
    """
    A dummy function.
    :return: None
    """

class AWSIntegration():
    """
    Represents base botocore event integration.
    """
    CLASS_TYPE = 'AWS'
    RESPONSE = {}
    OPERATION = {}

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """

        event_operation, _ = args
        scope.span.operation_name = str(event_operation)

        if response is not None:
            self.update_response(response, scope)

    def update_response(self, response, scope):
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """
        scope.span.status_code = response['ResponseMetadata']['HTTPStatusCode']
        scope.span.transaction_id = response['ResponseMetadata']['RequestId']


class AWSDynamoDBIntegration(AWSIntegration):
    """
    Represents DynamoDB integration.
    """
    CLASS_TYPE = 'dynamodb'

    def getStatementType(self, string):
        if string in Constants.DynamoDBRequestTypes:
            return Constants.DynamoDBRequestTypes[string]
        return 'READ'

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(AWSDynamoDBIntegration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        """
        super(AWSDynamoDBIntegration, self).update_response(response, scope)

    def process_get_item_op(self, scope):
        """
        Process the get item operation.
        """
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
    """
    Represents SQS integration.
    """
    CLASS_TYPE = 'sqs'

    def getRequestType(self, string):
        if string in Constants.SQSRequestTypes:
            return Constants.SQSRequestTypes[string]
        return 'READ'

    def getQueueName(self, data):
        if 'QueueUrl' in data:
            return data['QueueUrl'].split('/')[-1]
        elif 'QueueName' in data:
            return data['QueueName']

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(AWSSQSIntegration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        """
        super(AWSSQSIntegration, self).update_response(response, scope)


class AWSSNSIntegration(AWSIntegration):
    """
    Represents SNS integration.
    """
    CLASS_TYPE = 'sns'

    def getRequestType(self, string):
        if string in Constants.SNSRequestTypes:
            return Constants.SNSRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(AWSSNSIntegration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """

        super(AWSSNSIntegration, self).update_response(response, scope)


class AWSKinesisIntegration(AWSIntegration):
    """
    Represents kinesis botocore event.
    """
    CLASS_TYPE = 'kinesis'

    def getRequestType(self, string):
        if string in Constants.KinesisRequestTypes:
            return Constants.KinesisRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """

        super(AWSKinesisIntegration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """
        super(AWSKinesisIntegration, self).update_response(response, scope)


class AWSFirehoseIntegration(AWSIntegration):
    """
    Represents firehose botocore event.
    """
    CLASS_TYPE = 'firehose'

    def getRequestType(self, string):
        if string in Constants.FirehoseRequestTypes:
            return Constants.FirehoseRequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """

        super(AWSFirehoseIntegration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """
        super(AWSFirehoseIntegration, self).update_response(response, scope)


class AWSS3Integration(AWSIntegration):
    """
    Represents s3 botocore event.
    """

    CLASS_TYPE = 's3'

    def getRequestType(self, string):
        if string in Constants.S3RequestTypes:
            return Constants.S3RequestTypes[string]
        return Constants.AWS_SERVICE_REQUEST

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(AWSS3Integration, self).__init__(
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
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """
        super(AWSS3Integration, self).update_response(response, scope)

class AWSLambdaIntegration(AWSIntegration):
    """
    Represents lambda botocore event.
    """

    CLASS_TYPE = 'lambda'

    def getRequestType(self, string):
        if string in Constants.LambdaRequestType:
            return Constants.LambdaRequestType[string]
        return Constants.AWS_SERVICE_REQUEST

    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """

        super(AWSLambdaIntegration, self).__init__(
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


class AWSIntegrationFactory(object):
    """
    Factory class, generates botocore event.
    """

    INTEGRATIONS = {
        class_obj.CLASS_TYPE: class_obj
        for class_obj in AWSIntegration.__subclasses__()
    }

    @staticmethod
    def create_event(scope, wrapped, instance, args, kwargs, response,
                     exception):
        """
        Create an event according to the given instance_type.
        :param wrapped:
        :param instance:
        :param args:
        :param kwargs:
        :param start_time:
        :param response:
        :param exception:
        :return:
        """

        instance_type = instance.__class__.__name__.lower()
        event_class = AWSIntegrationFactory.INTEGRATIONS.get(
            instance_type,
            None
        )
        if event_class is not None:
            event = event_class(
                scope,
                wrapped,
                instance,
                args,
                kwargs,
                response,
                exception
            )
