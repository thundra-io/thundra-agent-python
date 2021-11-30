from thundra import constants

from thundra.opentracing.propagation.text import TextMapPropagator
from thundra.opentracing.span_context import ThundraSpanContext


class HTTPPropagator(TextMapPropagator):

    @staticmethod
    def extract_value_from_header(header_name, headers):
        for header, value in headers.items():
            if header.lower() == header_name.lower():
                return value

    def extract(self, carrier):
        try:
            trace_id = HTTPPropagator.extract_value_from_header(constants.THUNDRA_TRACE_ID_KEY, carrier)
            span_id = HTTPPropagator.extract_value_from_header(constants.THUNDRA_SPAN_ID_KEY, carrier)
            transaction_id = HTTPPropagator.extract_value_from_header(constants.THUNDRA_TRANSACTION_ID_KEY, carrier)
        except:
            return None

        if not (trace_id and span_id and transaction_id):
            return None

        # Extract baggage items
        baggage = {}
        for key in carrier:
            if isinstance(key, str):
                if key.startswith(constants.THUNDRA_BAGGAGE_PREFIX):
                    baggage[key[len(constants.THUNDRA_BAGGAGE_PREFIX):]] = carrier[key]
            elif isinstance(key, tuple):
                if key[0].startswith(constants.THUNDRA_BAGGAGE_PREFIX):
                    baggage[key[0][len(constants.THUNDRA_BAGGAGE_PREFIX):]] = key[1]

        span_context = ThundraSpanContext(trace_id=trace_id, span_id=span_id, transaction_id=transaction_id,
                                          baggage=baggage)

        return span_context
