import re
import traceback
import thundra.constants as constants
from thundra.listeners.thundra_span_listener import ThundraSpanListener
try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    xray_recorder = None


class AWSXRayListener(ThundraSpanListener):
    _data = None

    def __init__(self):
        self.xray_data = {}

    def _start_subsegment(self, span):
        subsegment_name = self._normalize_operation_name(span.operation_name)
        xray_recorder.begin_subsegment(subsegment_name)

    def on_span_started(self, span):
        if self.xray_available():
            span.tags[constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] = True
            self._start_subsegment(span)

    def _end_subsegment(self, span):
        if self.xray_available():
            xray_recorder.end_subsegment()

    def on_span_finished(self, span):
        if self.xray_available():
            self._add_metadata(span)
            self._add_annotation(span)
            self._add_error(span)
            self._end_subsegment(span)

    def _put_annotation_if_available(self, key, dictionary, dict_key, document):
        if dict_key in dictionary:
            value = dictionary[dict_key]
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
                document.put_annotation(self._normalize_annotation_name(key), self._normalize_annotation_value(value))

    def _add_annotation(self, span):
        self.xray_data = AWSXRayListener._data
        document = xray_recorder.current_subsegment()
        if document:
            document.put_annotation('traceId', span.context.trace_id)
            document.put_annotation('transactionId', span.context.transaction_id)
            document.put_annotation('spanId', span.context.span_id)
            document.put_annotation('parentSpanId', span.context.parent_span_id 
                if span.context.parent_span_id is not None else '')
            span_dict = vars(span)
            self._put_annotation_if_available('domainName', span_dict, 'domain_name', document)
            self._put_annotation_if_available('className', span_dict, 'class_name', document)
            self._put_annotation_if_available('operationName', span_dict, 'operation_name', document)
            self._put_annotation_if_available('startTimeStamp', span_dict, 'start_time', document)
            self._put_annotation_if_available('finishTimeStamp', span_dict, 'finish_time', document)
            duration = int(span.get_duration())
            document.put_annotation('duration', duration)

            if self.xray_data is not None:
                for key in self.xray_data:
                    self._put_annotation_if_available(key, self.xray_data, key, document)

    def _add_metadata(self, span):
        document = xray_recorder.current_subsegment()
        if document:
            for key in span.tags:
                document.put_metadata(key, span.tags[key])

    def _normalize_operation_name(self, operation_name):
        if operation_name:
            operation_name = re.sub(r'\s+', ' ', operation_name)
            operation_name = re.sub(r'[^\w\s\.:/%&#=+\\\-@]', '', operation_name)
            return operation_name[0:200]
        return constants.AwsXrayConstants['DEFAULT_OPERATION_NAME']

    def _normalize_annotation_value(self, value):
        if isinstance(value, str):
            value = value[0:1000]
        return value

    def _normalize_annotation_name(self, annotation_name):
        annotation_name = re.sub(r'\W+', '_', annotation_name)
        annotation_name = annotation_name[0:500]
        return annotation_name

    def _add_error(self, span):
        if span.get_tag('error'):
            document = xray_recorder.current_subsegment()
            if document:
                stack = traceback.extract_stack()
                document.add_exception(Exception(span.get_tag('error.message')), stack)

    @staticmethod
    def set_data(data):
        AWSXRayListener._data = data

    @staticmethod
    def xray_available():
        return xray_recorder is not None

    @staticmethod
    def get_xray_recorder():
        return xray_recorder
        
    @staticmethod
    def from_config(config):
        raise NotImplementedError
