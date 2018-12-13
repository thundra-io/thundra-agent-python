import thundra.constants as constants
import re
from thundra.listeners.thundra_span_listener import ThundraSpanListener
from thundra.opentracing.tracer import ThundraTracer
imported = True
try:
    from aws_xray_sdk.core import xray_recorder
except:
    imported = False
    print("AWS XRAY SDK NOT FOUND")
    # raise


class AWSXrayListener(ThundraSpanListener):

    _data = None
    _tracer = ThundraTracer.get_instance()

    def __init__(self):
        self.xray_data = {}

    def start_subsegment(self, span):
        xray_recorder.begin_subsegment(self.normalize_operation_name(span.operation_name))

    def on_span_started(self, span):
        if imported:
            span.tags[constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] = True
            self.start_subsegment(span)

    def end_subsegment(self, span):
        xray_recorder.end_subsegment()

    def on_span_finished(self, span):
        if imported:
            self.add_metadata(span)
            self.add_annotation(span)
            self.add_error(span)
            self.end_subsegment(span)

    def put_annotation_if_available(self, key, dictionary, dict_key, document):
        if dict_key in dictionary:
            value = dictionary[dict_key]
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
                document.put_annotation(self.normalize_annotation_name(key), self.normalize_annotation_value(value))

    def add_annotation(self, span):
        self.xray_data = AWSXrayListener._data
        document = xray_recorder.current_subsegment()
        if document:
            document.put_annotation('traceId', span.context.trace_id)
            document.put_annotation('transactionId', span.context.transaction_id)
            document.put_annotation('spanId', span.context.span_id)
            document.put_annotation('parentSpanId', span.context.parent_span_id)
            span_dict = vars(span)
            self.put_annotation_if_available('domainName', span_dict, 'domain_name', document)
            self.put_annotation_if_available('className', span_dict, 'class_name', document)
            self.put_annotation_if_available('operationName', span_dict, 'operation_name', document)
            self.put_annotation_if_available('startTimeStamp', span_dict, 'start_time', document)
            finish_time = int(span_dict['start_time']) + int(span_dict['duration'])
            document.put_annotation('finishTimeStamp', finish_time)
            self.put_annotation_if_available('duration', span_dict, 'duration', document)
            if self.xray_data is not None:
                for key in self.xray_data:
                    self.put_annotation_if_available(key, self.xray_data, key, document)

    def add_metadata(self, span):
        document = xray_recorder.current_subsegment()
        if document:
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

    def normalize_annotation_name(self, annotation_name):
        annotation_name = re.sub('/\./g', '_', annotation_name)
        annotation_name = re.sub('/[W]+/g', '', annotation_name)
        annotation_name = annotation_name[0:500]
        return annotation_name

    def add_error(self, span):
        if span.get_tag('error'):
            document = xray_recorder.current_subsegment()
            if document:
                document.add_exception(Exception(span.get_tag('error.message')))

    @staticmethod
    def set_data(data):
        AWSXrayListener._data = data
