import thundra.constants as constants
from thundra import utils
import re
import sys
import thundra.application_support as application_support
from thundra.listeners.thundra_span_listener import ThundraSpanListener
imported = True
try:
    from aws_xray_sdk.core import xray_recorder
except:
    imported = False
    print("AWS XRAY SDK NOT FOUND")
    raise


class AWSXrayListener(ThundraSpanListener):

    def __init__(self):
        pass

    # def before_invocation(self, plugin_context):
    #     context = plugin_context['context']
    #     function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
    #     app_tags = application_support.get_application_tags()
    #
    #     self.xray_data = {
    #         'applicationId': utils.get_application_id(context),
    #         'applicationName': function_name,
    #         'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
    #         'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
    #         'applicationRuntime': 'python',
    #         'applicationRuntimeVersion': str(sys.version_info[0]),
    #         'applicationTags': app_tags,
    #     }

    def on_span_started(self, span):
        if imported:
            span.tags[constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] = True
            return xray_recorder.begin_subsegment(self.normalize_operation_name(span.operation_name))

    def on_span_finished(self, span):
        if imported:
            self.add_metadata(span)
            self.add_annotation(span)
            self.add_error(span)
            return xray_recorder.end_subsegment()

    def put_annotation_if_available(self, key, dictionary, dict_key, document):
        if dict_key in dictionary:
            value = dictionary[dict_key]
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
                document.put_annotation(self.normalize_annotation_name(key), self.normalize_annotation_value(value))

    def add_annotation(self, span):
        document = xray_recorder.current_subsegment()
        document.put_annotation('traceId', span.context.trace_id)
        document.put_annotation('transactionId', span.context.transaction_id)
        document.put_annotation('spanId', span.context.span_id)
        document.put_annotation('parentSpanId', span.context.parent_span_id)
        span_dict = vars(span)
        self.put_annotation_if_available('domainName', span_dict, 'domain_name', document)
        self.put_annotation_if_available('className', span_dict, 'class_name', document)
        self.put_annotation_if_available('operationName', span_dict, 'operation_name', document)
        self.put_annotation_if_available('startTimeStamp', span_dict, 'start_time', document)
        finishTime = int(span_dict['start_time']) + int(span_dict['duration'])
        document.put_annotation('finishTimeStamp', finishTime)
        self.put_annotation_if_available('duration', span_dict, 'duration', document)
        print('Printing xray_data: ' + str(self.xray_data))
        for key in self.xray_data:
            self.put_annotation_if_available(key, self.xray_data[key], key, document)

    def add_metadata(self, span):
        document = xray_recorder.current_subsegment()
        for key in span.tags:
            document.put_metadata(key, span.tags[key])

    def normalize_operation_name(self, operation_name):
        if operation_name:
            return operation_name[0:200]
        return constants.AwsXrayConstants['DEFAULT_OPERATION_NAME']

    def normalize_annotation_value(self, value):
        if isinstance(value, str):
            value = value[0:1000]
        return value

    def normalize_annotation_name(self, annotationName):
        annotationName = re.sub('/\./g', '_', annotationName)
        annotationName = re.sub('/[W]+/g', '', annotationName)
        annotationName = annotationName[0:500]
        return annotationName

    def add_error(self, span):
        if span.get_tag('error'):
            document = xray_recorder.current_subsegment()
            document.add_exception(Exception(span.get_tag('error.message')))
