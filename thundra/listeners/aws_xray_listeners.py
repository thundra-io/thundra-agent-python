import re
import logging
import traceback
import thundra.constants as constants
from thundra.listeners.thundra_span_listener import ThundraSpanListener
try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    xray_recorder = None


logger = logging.getLogger(__name__)

class AWSXRayListener(ThundraSpanListener):
    def __init__(self):
        self.xray_data = {}

    def _start_subsegment(self, span):
        subsegment_name = self._normalize_operation_name(span.operation_name)
        xray_recorder.begin_subsegment(subsegment_name)

    def on_span_started(self, span):
        if self.xray_available():
            try:
                self._start_subsegment(span)
                span.tags[constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] = True
            except Exception as e:
                logger.error(("error occured while starting XRay subsegment "
                        "for span with name %s: %s"), span.operation_name, e)

    def _end_subsegment(self, span):
        if not span.get_tag(constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']):
            return
        
        try:
            subsegment = xray_recorder.current_subsegment()
            if subsegment is not None:
                self._add_metadata(subsegment, span)
                self._add_annotation(subsegment, span)
                self._add_error(subsegment, span)
                xray_recorder.end_subsegment()
        except Exception as e:
            logger.error(("error occured while ending XRay subsegment "
                          "for span with name %s: %s"), span.operation_name, e)
        finally:
            del span.tags[constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']]

    def on_span_finished(self, span):
        if self.xray_available():
            self._end_subsegment(span)

    def _put_annotation_if_available(self, key, dictionary, dict_key, document):
        if dict_key in dictionary:
            value = dictionary[dict_key]
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
                document.put_annotation(self._normalize_annotation_name(key), self._normalize_annotation_value(value))

    def _add_annotation(self, subsegment, span):
        subsegment.put_annotation('traceId', span.context.trace_id)
        subsegment.put_annotation('transactionId', span.context.transaction_id)
        subsegment.put_annotation('spanId', span.context.span_id)
        subsegment.put_annotation('parentSpanId', span.context.parent_span_id 
            if span.context.parent_span_id is not None else '')
        span_dict = vars(span)
        self._put_annotation_if_available('domainName', span_dict, 'domain_name', subsegment)
        self._put_annotation_if_available('className', span_dict, 'class_name', subsegment)
        self._put_annotation_if_available('operationName', span_dict, 'operation_name', subsegment)
        self._put_annotation_if_available('startTimeStamp', span_dict, 'start_time', subsegment)
        self._put_annotation_if_available('finishTimeStamp', span_dict, 'finish_time', subsegment)
        duration = int(span.get_duration())
        subsegment.put_annotation('duration', duration)

        if self.xray_data is not None:
            for key in self.xray_data:
                self._put_annotation_if_available(key, self.xray_data, key, subsegment)

    def _add_metadata(self, subsegment, span):
        for key in span.tags:
            subsegment.put_metadata(key, span.tags[key])

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

    def _add_error(self, subsegment, span):
        if span.get_tag('error'):
            stack = traceback.extract_stack()
            subsegment.add_exception(Exception(span.get_tag('error.message')), stack)

    @staticmethod
    def xray_available():
        return xray_recorder is not None

    @staticmethod
    def get_xray_recorder():
        return xray_recorder
        
    @staticmethod
    def from_config(config):
        raise NotImplementedError

    @staticmethod
    def should_raise_exceptions():
        return False
