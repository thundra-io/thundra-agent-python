from foresight.test_runner_support import TestRunnerSupport
from foresight.test_runner_tags import TestRunnerTags
from foresight.environment.environment_info_support import EnvironmentSupport
from foresight.utils.test_wrapper_utils import TestWrapperUtils
import logging

logger = logging.getLogger(__name__)

def start_trace(plugin_context, execution_context, tracer):
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.start_trace(execution_context, tracer)
        
        root_span = execution_context.root_span
        test_run_scope = TestRunnerSupport.test_run_scope

        root_span.set_tag(TestRunnerTags.TEST_RUN_ID, test_run_scope.id)
        root_span.set_tag(TestRunnerTags.TEST_RUN_TASK_ID, test_run_scope.task_id)

        root_span.tags.update(execution_context.get_additional_start_tags())

        EnvironmentSupport.set_span_tags(root_span)
    except Exception as err:
        logger.error("foresight executor start trace error", err)


def finish_trace(execution_context):
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.finish_trace(execution_context)

        root_span = execution_context

        root_span.tags.update(execution_context.get_additional_finish_tags())
    except Exception as err:
        logger.error("foresight eecutor finish trace error", err)


def start_invocation(plugin_context, execution_context):
    try:
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.start_invocation(execution_context)
        
        execution_context.invocation_data["tags"].update(execution_context.get_additional_start_tags())
    except Exception as err:
        logger.error("foresight executor start incovation error", err)


def finish_invocation(execution_context):
    try:
        invocation_data = execution_context.invocation_data

        test_wrapper_utils = TestWrapperUtils.get_instance()
        
        test_run_scope = TestRunnerSupport.test_run_scope 

        invocation_data["tags"][TestRunnerTags.TEST_RUN_ID] = test_run_scope.id
        invocation_data["tags"][TestRunnerTags.TEST_RUN_TASK_ID] = test_run_scope.task_id

        invocation_data["tags"].update(execution_context.get_additional_finish_tags())

        error = execution_context.error
        if error:
            invocation_data['tags']['error.type'] = error.get('type')
            invocation_data['tags']['error.message'] = error.get('message')
            invocation_data['tags']['error.stack'] = error.get('traceback', None)

        EnvironmentSupport.set_invocation_tags(invocation_data)  
        test_wrapper_utils.finish_invocation(execution_context)
    except Exception as err:
        logger.error("foresight executor finish invocation error", err)