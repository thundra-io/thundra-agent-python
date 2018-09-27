import os
from thundra import constants
from thundra.plugins.trace.patcher import ImportPatcher

target_function_prefix = "get"
target_module_name = "...testdemo.movie_service.MovieService"
target_trace_arguments = "[trace_args=True]"
target_trace_arguments_list = ['trace_args']


def test_retrieving_function_prefix(monkeypatch):
        monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG,\
                         "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
        patcher = ImportPatcher()

        assert patcher.get_module_function_prefix(target_module_name) == target_function_prefix


def test_retrieving_trace_args(monkeypatch):
        monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_CONFIG,\
                         "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
        patcher = ImportPatcher()
        for arg in patcher.get_trace_arguments(target_module_name):
                assert arg in target_trace_arguments_list
