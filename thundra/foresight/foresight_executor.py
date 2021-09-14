from thundra.foresight.test_runner_support import TestRunnerSupport
from thundra.foresight.test_runner_tags import TestRunnerTags
from thundra.foresight.environment.environment_info_support import EnvironmentSupport
import thundra.wrappers.wrapper_utils as wrapper_utils
from uuid import uuid4


def start_trace(plugin_context, execution_context, tracer):
    trace_id = str(uuid4)
    operation_name = execution_context.get_operation_name()
    scope = tracer.start_active_span(
        operation_name=operation_name,
        start_time=execution_context.start_timestamp,
        finish_on_close=False,
        trace_id=trace_id,
        transaction_id=execution_context.transaction_id,
        execution_context=execution_context
    )
    root_span = scope.span
    root_span.class_name = plugin_context.get("applicationClassName")
    root_span.domain_name = plugin_context.get("applicationDomainName")
    execution_context.span_id = root_span.context.span_id
    execution_context.root_span = root_span
    execution_context.scope = scope
    execution_context.trace_id = trace_id
    
    root_span = execution_context.root_span
    test_run_scope = TestRunnerSupport.test_run_scope

    root_span.set_tag(TestRunnerTags.TEST_RUN_ID, test_run_scope.id)
    root_span.set_tag(TestRunnerTags.TEST_RUN_TASK_ID, test_run_scope.task_id)

    root_span.tags.update(execution_context.get_additional_start_tags())

    EnvironmentSupport.set_tags(root_span)


def finish_trace(execution_context):
    root_span = execution_context.root_span
    scope = execution_context.scope
    try:
        root_span.finish(f_time=execution_context.finish_timestamp)
    except Exception:
        # TODO: handle root span finish errors
        pass
    finally:
        scope.close()

    root_span = execution_context

    root_span.tags.update(execution_context.get_additional_finish_tags())


def start_invocation(plugin_context, execution_context):
    execution_context.invocation_data = wrapper_utils.create_invocation_data(plugin_context, execution_context)

    execution_context.invocation_data.update(execution_context.get_additional_tags())


def finish_invocation(execution_context):
    invocation_data = execution_context.invocation_data

    wrapper_utils.finish_invocation(execution_context)

    test_run_scope = TestRunnerSupport.test_run_scope 

    invocation_data.tags[TestRunnerTags.TEST_RUN_ID] = test_run_scope.id
    invocation_data.tags[TestRunnerTags.TEST_RUN_TASK_ID] = test_run_scope.task_id

    invocation_data.tags.update(execution_context.get_additional_finish_tags())

    EnvironmentSupport.set_tags(invocation_data)   