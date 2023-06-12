from opentracing import InvalidCarrierException

from catchpoint import constants
from catchpoint.opentracing.propagation.propagator import Propagator
from catchpoint.opentracing.span_context import CatchpointSpanContext


class TextMapPropagator(Propagator):

    def inject(self, span_context, carrier):
        if span_context.trace_id:
            carrier[constants.CATCHPOINT_TRACE_ID_KEY] = span_context.trace_id

        if span_context.span_id:
            carrier[constants.CATCHPOINT_SPAN_ID_KEY] = span_context.span_id

        if span_context.transaction_id:
            carrier[constants.CATCHPOINT_TRANSACTION_ID_KEY] = span_context.transaction_id

        # Inject baggage items
        if span_context.baggage is not None:
            for key in span_context.baggage:
                carrier[constants.CATCHPOINT_BAGGAGE_PREFIX + key] = span_context.baggage[key]

    def extract(self, carrier):
        try:
            trace_id = carrier[constants.CATCHPOINT_TRACE_ID_KEY]
            span_id = carrier[constants.CATCHPOINT_SPAN_ID_KEY]
            transaction_id = carrier[constants.CATCHPOINT_TRANSACTION_ID_KEY]
        except:
            return None

        if not (trace_id and span_id and transaction_id):
            return None

        # Extract baggage items
        baggage = {}
        for key in carrier:
            if key.startswith(constants.CATCHPOINT_BAGGAGE_PREFIX):
                baggage[key[len(constants.CATCHPOINT_BAGGAGE_PREFIX):]] = carrier[key]

        span_context = CatchpointSpanContext(trace_id=trace_id, span_id=span_id, transaction_id=transaction_id,
                                             baggage=baggage)

        return span_context
