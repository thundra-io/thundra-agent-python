from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

target_function_prefix = "get"
target_module_name = "...testdemo.movie_service.MovieService"
target_trace_arguments = "[trace_args=True]"
target_trace_arguments_list = ['trace_args']

from thundra.compat import PY2

if not PY2:
        from thundra.plugins.trace.patcher import ImportPatcher

        def test_retrieving_function_prefix():
                ConfigProvider.set(config_names.THUNDRA_TRACE_INSTRUMENT_TRACEABLECONFIG, \
                        "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
                patcher = ImportPatcher()

                assert patcher.get_module_function_prefix(target_module_name) == target_function_prefix


        def test_retrieving_trace_args():
                ConfigProvider.set(config_names.THUNDRA_TRACE_INSTRUMENT_TRACEABLECONFIG, \
                        "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
                patcher = ImportPatcher()
                for arg in patcher.get_trace_arguments(target_module_name):
                        assert arg in target_trace_arguments_list
