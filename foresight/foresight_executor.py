from foresight.test_runner_support import TestRunnerSupport
from foresight.test_runner_tags import TestRunnerTags
from foresight.environment.environment_info_support import EnvironmentSupport
from foresight.utils.test_wrapper_utils import TestWrapperUtils
import logging

logger = logging.getLogger(__name__)

def start_trace(plugin_context, execution_context, tracer):
    """Start trace plugin. It is executed by hook in BaseWrapper

    Args:
        plugin_context (PluginContext): Stores thundra plugins' contexts
        execution_context (TestCaseExecutionContext | TestSuiteExecutionContext): Stores Execution context info
        tracer (ThundraTracer): Thundra scope tracer
    """
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.start_trace(execution_context, tracer)
        
        root_span = execution_context.root_span

        root_span.tags.update(execution_context.get_additional_start_tags())

        EnvironmentSupport.set_span_tags(root_span)
    except Exception as err:
        logger.error("Foresight executor start trace error {}".format(err))
        pass

def finish_trace(execution_context):
    """Finish trace plugin. It is executed by hook in BaseWrapper

    Args:
        execution_context (TestCaseExecutionContext | TestSuiteExecutionContext): Stores Execution context info
    """
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.finish_trace(execution_context)

        root_span = execution_context

        root_span.tags.update(execution_context.get_additional_finish_tags())
    except Exception as err:
        logger.error("foresight eecutor finish trace error: {}".format(err))
        pass

def start_invocation(plugin_context, execution_context):
    """Start invocation for thundra invocation plugin.It is executed by hook in BaseWrapper

    Args:
        plugin_context (PluginContext): Stores thundra plugins' contexts
        execution_context (TestCaseExecutionContext | TestSuiteExecutionContext): Stores Execution context info
    """
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.start_invocation(execution_context)
        
        execution_context.invocation_data["tags"].update(execution_context.get_additional_start_tags())
    except Exception as err:
        logger.error("foresight executor start incovation error: {}".format(err))
        pass

def finish_invocation(execution_context):    
    """Finish invocation for thundra invocation plugin.It is executed by hook in BaseWrapper

    Args:
        execution_context (TestCaseExecutionContext | TestSuiteExecutionContext): Stores Execution context info
    """
    try:
        invocation_data = execution_context.invocation_data

        test_wrapper_utils = TestWrapperUtils.get_instance()

        invocation_data["tags"].update(execution_context.get_additional_finish_tags())

        error = execution_context.error
        if error:
            invocation_data['tags']['error.type'] = error.get('type')
            invocation_data['tags']['error.message'] = error.get('message')
            invocation_data['tags']['error.stack'] = error.get('traceback', None)

        EnvironmentSupport.set_invocation_tags(invocation_data)  
        test_wrapper_utils.finish_invocation(execution_context)
    except Exception as err:
        logger.error("Foresight executor finish invocation error: {}".format(err))
        pass