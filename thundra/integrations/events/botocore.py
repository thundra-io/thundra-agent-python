from __future__ import absolute_import

import hashlib
import traceback
import simplejson as json
import thundra.constants as Constants
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from ..base_integration import BaseIntegration
from thundra.opentracing.tracer import ThundraTracer


# pylint: disable=W0613
def dummy_func(*args):
    """
    A dummy function.
    :return: None
    """


class AWSIntegration(BaseIntegration):
    """
    Represents base botocore event.
    """

    CLASS_TYPE = 'AWS'
    RESPONSE = {}
    OPERATION = {}

    # pylint: disable=W0613
    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param start_time: Start timestamp (epoch)
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(AWSIntegration, self).__init__()

        event_operation, _ = args

        scope.__getattribute__('_span').__setattr__('operationName', str(event_operation))
        # scope.__getattribute__('_span').__setattr__('domainName', Constants.DomainNames['AWS'])
        # scope.__getattribute__('_span').__setattr__('className', Constants.ClassNames['AWSSERVICE'])
        # scope.__getattribute__('_span').__setattr__('operation_name', Constants.AWS_SERVICE_REQUEST)

        if response is not None:
            self.update_response(response, scope)

        if exception is not None:
            self.set_exception(exception, traceback.format_exc(), scope)

    def set_exception(self, exception, traceback_data, scope):
        """
        Sets exception data on event.
        :param exception: Exception object
        :param traceback_data: traceback string
        :return: None
        """
        super(AWSIntegration, self).set_exception(exception, traceback_data, scope)

        # Specific handling for botocore errors
        if isinstance(exception, ClientError):
            self.event_id = exception.response['ResponseMetadata']['RequestId']
            botocore_error = exception.response['Error']
            scope.__getattribute__('_span').__setattr__('error', True)
            scope.__getattribute__('_span').__setattr__('errorCode', str(botocore_error.get('Code', '')))
            scope.__getattribute__('_span').__setattr__('errorMessage', str(botocore_error.get('Message', '')))
            scope.__getattribute__('_span').__setattr__('errorType', str(botocore_error.get('Type', '')))

    def update_response(self, response, scope):
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """
        scope.__getattribute__('_span').__setattr__('statusCode', response['ResponseMetadata']['HTTPStatusCode'])
        scope.__getattribute__('_span').__setattr__('transactionId', response['ResponseMetadata']['RequestId'])


class AWSDynamoDBListener(AWSIntegration):
    """
    Represents DynamoDB botocore event.
    """
    CLASS_TYPE = 'dynamodb'

    def getStatementType(self, str):
        if str in Constants.DynamoDBRequestTypes:
            return Constants.DynamoDBRequestTypes[str]
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
        super(AWSDynamoDBListener, self).__init__(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )

        self.RESPONSE.update(
            {'Scan': self.process_scan_response,
             'GetItem': self.process_get_item_response,
             'ListTables': self.process_list_tables_response}
        )

        self.OPERATION.update(
            {'PutItem': self.process_put_item_op,
             'UpdateItem': self.process_update_item_op,
             'GetItem': self.process_get_item_op,
             'DeleteItem': self.process_delete_item_op,
             'BatchWriteItem': self.process_batch_write_op,
             }
        )

        operationName, request_data = args
        self.request_data = request_data
        self.response = response

        scope.__getattribute__('_span').__setattr__('domainName', Constants.DomainNames['DB'])
        scope.__getattribute__('_span').__setattr__('className', Constants.ClassNames['DYNAMODB'])
        scope.__getattribute__('_span').__setattr__('operation_name',
                                                    'dynamodb: ' + str(self.request_data['TableName']))
        ## ADDING TAGS ##

        tags = {
            Constants.SpanTags['SPAN_TYPE']: Constants.SpanTypes['AWS_DYNAMO'],
            Constants.SpanTags['OPERATION_TYPE']: self.getStatementType(operationName),
            Constants.DBTags['DB_TYPE']: Constants.DBTypes['DYNAMODB'],
            Constants.AwsDynamoTags['TABLE_NAME']: str(self.request_data['TableName']),
            Constants.DBTags['DB_STATEMENT_TYPE']: self.getStatementType(operationName),
            Constants.AwsSDKTags['REQUEST_NAME']: operationName,
        }
        scope.__getattribute__('_span').__setattr__('tags', tags)

        ## FINISHED ADDING TAGS ##
        self.OPERATION.get(operationName, dummy_func)(scope)

    def update_response(self, response, scope):
        """
        Adds response data to event.
        :param response: Response from botocore
        """
        super(AWSDynamoDBListener, self).update_response(response, scope)

    def process_get_item_op(self, scope):
        """
        Process the get item operation.
        """
        # self.resource['name'] = self.request_data['TableName']
        scope.__getattribute__('_span').__getattribute__('tags')[Constants.DBTags['DB_STATEMENT']] = \
            self.request_data['Key']
        print("Printing tags ", str(scope.__getattribute__('_span').__getattribute__('tags')))
        # self.resource['metadata']['Key'] = self.request_data['Key']

    def process_put_item_op(self, scope):
        if 'Item' in self.request_data:
            scope.__getattribute__('_span').__getattribute__('tags')[Constants.DBTags['DB_STATEMENT']] = \
                self.request_data['Item']
            item = self.request_data['Item']
            self.store_item_hash(item)

    def process_delete_item_op(self, scope):
        scope.__getattribute__('_span').__getattribute__('tags')[Constants.DBTags['DB_STATEMENT']] = \
            self.request_data['Key']

    def process_update_item_op(self, scope):
        scope.__getattribute__('_span').__getattribute__('tags')[Constants.DBTags['DB_STATEMENT']] = \
            self.request_data['Key']
        # self.resource['metadata']['Update Parameters'] = {
        #     'Key': self.request_data['Key'],
        #     'Expression Attribute Values': self.request_data.get(
        #         'ExpressionAttributeValues', None),
        #     'Update Expression': self.request_data.get(
        #         'UpdateExpression',
        #         None
        #     ),
        # }

    def process_batch_write_op(self, scope):
            table_name = list(self.request_data['RequestItems'].keys())[0]
            self.resource['name'] = table_name
            items = []
            for item in self.request_data['RequestItems'][table_name]:
                items.append(item)

            scope.__getattribute__('_span').__getattribute__('tags')[Constants.DBTags['DB_STATEMENT']] =\
                items

    def process_scan_response(self):
            """
            Process the scan response.
            """
            self.resource['name'] = self.request_data['TableName']
            self.resource['metadata']['Items Count'] = self.response['Count']
            self.resource['metadata']['Scanned Items Count'] = \
                self.response['ScannedCount']

    def process_get_item_response(self):
            """
            Process the get item response.
            :return:
            """
            self.resource['name'] = self.request_data['TableName']

    def process_list_tables_response(self):
            """
            Process the list tables response.
            :return:
            """
            self.resource['name'] = 'DynamoDBEngine'
            self.resource['metadata']['Table Names'] = \
                ', '.join(self.response['TableNames'])

    def store_item_hash(self, item):
            """
            Store the item hash in the metadata.
            :param item: The item to store the hash for.
            """
            deserializer = TypeDeserializer()

            # Try to deserialize the data in order to remove dynamoDB data types.
            for key in item:
                try:
                    item[key] = deserializer.deserialize(item[key])
                except (TypeError, AttributeError):
                    break
            self.resource['metadata']['item_hash'] = hashlib.md5(
                json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()


class AWSEventListeners(object):
    """
    Factory class, generates botocore event.
    """

    FACTORY = {
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
        event_class = AWSEventListeners.FACTORY.get(
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
