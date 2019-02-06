import re
import logging
import traceback
from thundra import constants, application_support
from thundra.listeners.thundra_span_listener import ThundraSpanListener
try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    xray_recorder = None


logger = logging.getLogger(__name__)

class AWSXRayListener(ThundraSpanListener):
    def __init__(self):
        pass
    
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

    def _add_annotation(self, subsegment, span):
        span_dict = vars(span)
        annotations = {
            'traceId': span.context.trace_id,
            'transactionId': span.context.transaction_id,
            'spanId': span.context.span_id,
            'parentSpanId': span.context.parent_span_id,
            'duration': span.get_duration(),
            'domainName': span_dict.get('domain_name'),
            'className': span_dict.get('class_name'),
            'operationName': span_dict.get('operation_name'),
            'startTimeStamp': span_dict.get('start_time'),
            'finishTimeStamp': span_dict.get('finish_time'),
        }

        # Add application related data
        application_info = application_support.get_application_info()
        annotations.update(application_info)

        # Normalize each key and value and add to the subsegment
        for k, v in annotations.items():
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, bool):
                subsegment.put_annotation(self._normalize_annotation_name(k), self._normalize_annotation_value(v))
            

    def _add_metadata(self, subsegment, span):
        for k, v in span.tags.items():
            subsegment.put_metadata(k, v)

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
