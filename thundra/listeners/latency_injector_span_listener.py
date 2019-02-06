import time
import random
import logging
from thundra import constants, utils
from thundra.listeners.thundra_span_listener import ThundraSpanListener

logger = logging.getLogger(__name__)

class LatencyInjectorSpanListener(ThundraSpanListener):
    available_distributions = ["normal", "uniform"]

    def __init__(self, delay=0, variation=0, 
                 sigma=0, distribution="uniform", 
                add_info_tags=True):
        self.delay = max(0, delay)
        self.sigma = max(0, sigma)
        self.variation = max(0, variation)
        self.add_info_tags = add_info_tags
        if distribution in self.available_distributions:
            self.distribution = distribution
        else:
            self.distribution = "uniform"
        
    def on_span_started(self, span):
        self._inject_delay(span)

    def on_span_finished(self, span):
        pass

    def _inject_delay(self, span):
        delay = self._calculate_delay()
        if delay != 0:
            if self.add_info_tags:
                self._add_info_tags(span, delay)
            time.sleep(delay / 1000.0)
    
    def _calculate_delay(self):
        delay = self.delay
        if self.distribution == "uniform" and self.variation != 0:
            delay = random.randint(self.delay-self.variation, self.delay+self.variation)
        elif self.distribution == "normal" and self.sigma != 0:
            delay = round(random.gauss(self.delay, self.sigma))
        
        return max(0, delay)
    
    def _add_info_tags(self, span, injected_delay):
        try:
            info_dict = {
                'type': 'latency_injector_span_listener',
                'injected_delay': injected_delay,
                'delay': self.delay,
                'variation': self.variation,
                'sigma': self.sigma,
                'distribution': self.distribution,
            }
            span.set_tag(constants.THUNDRA_LAMBDA_SPAN_LISTENER_INFO_TAG, info_dict)
        except Exception as e:
            logger.error("error while adding LatencyInjectorSpanListener info tags: %s", e)

    @staticmethod
    def from_config(config):
        kwargs = {}
        delay = config.get('delay')
        variation = config.get('variation')
        sigma = config.get('sigma')
        distribution = config.get('distribution')
        add_info_tags = config.get('addInfoTags')

        if delay is not None:
            try:
                kwargs['delay'] = int(delay)
            except ValueError:
                LatencyInjectorSpanListener._log_value_parse_err(delay, 'delay')
        if variation is not None:
            try:
                kwargs['variation'] = int(variation)
            except ValueError:
                LatencyInjectorSpanListener._log_value_parse_err(variation, 'variation')
        if sigma is not None:
            try:
                kwargs['sigma'] = int(sigma)
            except ValueError:
                LatencyInjectorSpanListener._log_value_parse_err(sigma, 'sigma')
        if distribution is not None:
            try:
                kwargs['distribution'] = str(distribution)
            except ValueError:
               LatencyInjectorSpanListener._log_value_parse_err(distribution, 'distribution')
        if add_info_tags is not None:
            try:
                kwargs['add_info_tags'] = utils.str2bool(add_info_tags)
            except ValueError:
                LatencyInjectorSpanListener._log_value_parse_err(add_info_tags, 'add_info_tags')
    
        return LatencyInjectorSpanListener(**kwargs)
    
    @staticmethod
    def _log_value_parse_err(param, param_name):
        logger.error(("couldn't parse %s parameter (%s) of "
            "LatencyInjectorSpanListener, using the default value"), param_name, param)

            
    @staticmethod
    def should_raise_exceptions():
        return False
        
