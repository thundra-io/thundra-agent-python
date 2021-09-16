from thundra.foresight.test_runner_support import TestRunnerSupport
from thundra.foresight.test_runner_tags import TestRunnerTags
from thundra.foresight.environment.environment_info_support import EnvironmentSupport
from thundra.foresight.util.test_wrapper_utils import TestWrapperUtils
from uuid import uuid4


def start_trace(plugin_context, execution_context, tracer):
    test_wrapper_utils = TestWrapperUtils.get_instance()
    test_wrapper_utils.start_trace(execution_context, tracer)
    
    root_span = execution_context.root_span
    test_run_scope = TestRunnerSupport.test_run_scope

    root_span.set_tag(TestRunnerTags.TEST_RUN_ID, test_run_scope.id)
    root_span.set_tag(TestRunnerTags.TEST_RUN_TASK_ID, test_run_scope.task_id)

    root_span.tags.update(execution_context.get_additional_start_tags())

    EnvironmentSupport.set_span_tags(root_span)


def finish_trace(execution_context):

    test_wrapper_utils = TestWrapperUtils.get_instance()
    test_wrapper_utils.finish_trace(execution_context)

    root_span = execution_context

    root_span.tags.update(execution_context.get_additional_finish_tags())


def start_invocation(plugin_context, execution_context):
    test_wrapper_utils = TestWrapperUtils.get_instance()
    test_wrapper_utils.start_invocation(execution_context)
    
    execution_context.invocation_data["tags"].update(execution_context.get_additional_start_tags())


def finish_invocation(execution_context):
    invocation_data = execution_context.invocation_data

    test_wrapper_utils = TestWrapperUtils.get_instance()
    test_wrapper_utils.finish_invocation(execution_context)
    
    test_run_scope = TestRunnerSupport.test_run_scope 

    invocation_data["tags"][TestRunnerTags.TEST_RUN_ID] = test_run_scope.id
    invocation_data["tags"][TestRunnerTags.TEST_RUN_TASK_ID] = test_run_scope.task_id

    invocation_data["tags"].update(execution_context.get_additional_finish_tags())

    EnvironmentSupport.set_invocation_tags(invocation_data)   