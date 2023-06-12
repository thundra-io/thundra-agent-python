from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names

target_function_prefix = "get"
target_module_name = "...testdemo.movie_service.MovieService"
target_trace_arguments = "[trace_args=True]"
target_trace_arguments_list = ['trace_args']

from catchpoint.compat import PY2

if not PY2:
        from catchpoint.plugins.trace.patcher import ImportPatcher
        import pytest

        @pytest.mark.skip(reason="This functionality not in use!")
        def test_retrieving_function_prefix():
                ConfigProvider.set(config_names.CATCHPOINT_TRACE_INSTRUMENT_TRACEABLECONFIG, \
                        "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
                patcher = ImportPatcher()

                assert patcher.get_module_function_prefix(target_module_name) == target_function_prefix


        @pytest.mark.skip(reason="This functionality not in use!")
        def test_retrieving_trace_args():
                ConfigProvider.set(config_names.CATCHPOINT_TRACE_INSTRUMENT_TRACEABLECONFIG, \
                        "{}.{}*{}".format(target_module_name ,target_function_prefix, target_trace_arguments))
                patcher = ImportPatcher()
                for arg in patcher.get_trace_arguments(target_module_name):
                        assert arg in target_trace_arguments_list
