from __future__ import absolute_import

from importlib import import_module as _import_module

import catchpoint.integrations.modules as integrations
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.opentracing.tracer import CatchpointTracer
from catchpoint.plugins.invocation.invocation_support import (
    set_tag,
    set_tags,
    remove_tag,
    get_tag,
    get_tags,
    set_error,
    clear_error
)
from catchpoint.plugins.invocation.invocation_trace_support import (
    add_incoming_trace_link,
    add_incoming_trace_links,
    add_outgoing_trace_link,
    add_outgoing_trace_links,
    get_incoming_trace_links,
    get_outgoing_trace_links,
)
from catchpoint.plugins.log import log_support as log
from catchpoint.plugins.metric import metric_support as metric
from catchpoint.plugins.trace import trace_support as trace
from catchpoint.plugins.trace.trace_aware_wrapper import TraceAwareWrapper
from catchpoint.plugins.trace.traceable import Traceable
from catchpoint.wrappers.wrapper_factory import WrapperFactory as _WrapperFactory

import logging
logger = logging.getLogger(__name__)

def _import_exists(module_name):
    try:
        _import_module(module_name)
        return True
    except ImportError:
        return False


def _patch_modules():
    for module_name, module in integrations.MODULES.items():
        if _import_exists(module_name):
            if hasattr(module, "patch"):
                try:
                    module.patch()
                except Exception as e:
                    logger.error("Couldn't patch module: %s", e)


def configure(options=None):
    ConfigProvider.__init__(options)


def lambda_wrapper(func):
    from catchpoint.wrappers.aws_lambda.lambda_wrapper import LambdaWrapper
    return _WrapperFactory.get_or_create(LambdaWrapper)(func)


def django_wrapper(func):
    from catchpoint.wrappers.django.django_wrapper import DjangoWrapper
    return _WrapperFactory.get_or_create(DjangoWrapper)(func)


def flask_wrapper(func):
    from catchpoint.wrappers.flask.flask_wrapper import FlaskWrapper
    return _WrapperFactory.get_or_create(FlaskWrapper)(func)


def fastapi_wrapper(func):
    from catchpoint.wrappers.fastapi.fastapi_wrapper import FastapiWrapper
    return _WrapperFactory.get_or_create(FastapiWrapper)(func)


def tornado_wrapper(func):
    from catchpoint.wrappers.tornado.tornado_wrapper import TornadoWrapper
    return _WrapperFactory.get_or_create(TornadoWrapper)(func)


def _set_catchpoint_for_test_env(already_configured):
    if not already_configured:
        configure()
    if not ConfigProvider.get(config_names.CATCHPOINT_DISABLE):
        _patch_modules()


if not ConfigProvider.get(config_names.CATCHPOINT_DISABLE):
    test_active = ConfigProvider.get(config_names.CATCHPOINT_TEST_ACTIVE)
    if not test_active:
        _patch_modules()


__all__ = [
    'configure',
    'TraceAwareWrapper',
    'log',
    'metric',
    'trace',
    'lambda_wrapper',
    'django_wrapper',
    'flask_wrapper',
    'fastapi_wrapper',
    'tornado_wrapper',
    'add_incoming_trace_link',
    'add_incoming_trace_links',
    'add_outgoing_trace_link',
    'add_outgoing_trace_links',
    'get_incoming_trace_links',
    'get_outgoing_trace_links',
    'set_tag',
    'set_tags',
    'remove_tag',
    'get_tag',
    'get_tags',
    'set_error',
    'clear_error',
    'Traceable'
]
