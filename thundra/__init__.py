from __future__ import absolute_import

from importlib import import_module

import thundra.integrations.modules as integrations
from thundra import _version
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.plugins.invocation import invocation_support
from thundra.plugins.log import log_support
from thundra.plugins.metric import metric_support
from thundra.plugins.trace import trace_support
from thundra.wrappers.aws_lambda.lambda_wrapper import LambdaWrapper

__version__ = _version.__version__


def _import_exists(module_name):
    try:
        import_module(module_name)
        return True
    except ImportError:
        return False


def patch_modules():
    for module_name, module in integrations.MODULES.items():
        if _import_exists(module_name):
            module.patch()


if not ConfigProvider.get(config_names.THUNDRA_DISABLE):
    patch_modules()
