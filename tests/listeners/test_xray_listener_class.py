from thundra.listeners.aws_xray_listeners import AWSXRayListener
from thundra.opentracing.tracer import ThundraTracer
from aws_xray_sdk.core import xray_recorder


class AWSXRayListenerTesting(AWSXRayListener):

    _tracer = ThundraTracer.get_instance()

    def __init__(self):
        super(AWSXRayListenerTesting, self).__init__()

    def start_subsegment(self, span):
        super(AWSXRayListenerTesting, self).start_subsegment(span)

    def on_span_started(self, span):
        super(AWSXRayListenerTesting, self).on_span_started(span)

    def end_subsegment(self, span):
        dict_recorder = {'xray': vars(xray_recorder.current_subsegment()), 'span': vars(span)}
        AWSXRayListenerTesting._tracer.test_xray_traces.append(dict_recorder)
        super(AWSXRayListenerTesting, self).end_subsegment(span)

    def on_span_finished(self, span):
        self.add_metadata(span)
        self.add_annotation(span)
        self.add_error(span)
        self.end_subsegment(span)

    def put_annotation_if_available(self, key, dictionary, dict_key, document):
        super(AWSXRayListenerTesting, self).put_annotation_if_available(key, dictionary, dict_key, document)

    def add_annotation(self, span):
        super(AWSXRayListenerTesting, self).add_annotation(span)

    def add_metadata(self, span):
        super(AWSXRayListenerTesting, self).add_metadata(span)

    def normalize_operation_name(self, operation_name):
        return super(AWSXRayListenerTesting, self).normalize_operation_name(operation_name)

    def normalize_annotation_value(self, value):
        if isinstance(value, str):
            value = value[0:1000]
        return value

    def normalize_annotation_name(self, annotation_name):
        return super(AWSXRayListenerTesting, self).normalize_operation_name(annotation_name)

    def add_error(self, span):
        super(AWSXRayListenerTesting, self).add_error(span)

    @staticmethod
    def set_data(data):
        AWSXRayListener._data = data