from thundra.opentracing.tracer import ThundraTracer
from thundra import constants
try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    xray_recorder = None
from thundra.plugins.trace import trace_support
import pytest


def test_annotation_metadata_and_tags(handler_with_xray_testing, mock_event, mock_context):
    if xray_recorder is not None:
        try:
            thundra, handler = handler_with_xray_testing
            tracer = ThundraTracer.get_instance()
            handler(mock_event, mock_context)
            xray_recorder.end_segment()
            data = thundra.plugins[-1].xray_listener.test_data
            xray = data['xray']
            span = data['span']
            # Testing span values
            assert xray['name'] == span['operation_name']
            assert constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME'] in span['tags']
            # Testing annotation values
            assert xray['annotations']['spanId'] == span['_context'].span_id
            assert xray['annotations']['applicationVersion'] == 'function_version'
            assert xray['annotations']['applicationRuntime'] == 'python'
            assert xray['annotations']['applicationRuntimeVersion'] == '3'
            assert xray['annotations']['applicationStage'] == 'dev'
            # Testing metadata
            assert xray['metadata']['default'][constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] == True
        except Exception as e:
            raise e
        finally:
            data.clear()
            trace_support.clear_span_listeners()
            tracer.clear()
