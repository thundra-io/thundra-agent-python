import time
import random
from thundra.listeners.thundra_span_listener import ThundraSpanListener


class LatencyInjectorSpanListener(ThundraSpanListener):
    available_distributions = ["normal", "uniform"]

    def __init__(self, delay=0, variation=0, sigma=0, distribution="uniform"):
        self.delay = max(0, delay)
        self.sigma = max(0, sigma)
        self.variation = max(0, variation)
        if distribution in self.available_distributions:
            self.distribution = distribution
        else:
            self.distribution = "uniform"
        
    def on_span_started(self, span):
        self._inject_delay()

    def on_span_finished(self, span):
        pass

    def _inject_delay(self):
        delay = self._calculate_delay()
        if delay != 0:
            time.sleep(delay / 1000.0)
    
    def _calculate_delay(self):
        delay = self.delay
        if self.distribution == "uniform" and self.variation != 0:
            delay = random.randint(self.delay-self.variation, self.delay+self.variation)
        elif self.distribution == "normal" and self.sigma != 0:
            delay = round(random.gauss(self.delay, self.sigma))
        
        return max(0, delay)

    @staticmethod
    def from_config(config):
        kwargs = {}
        delay = config.get('delay')
        variation = config.get('variation')
        sigma = config.get('sigma')
        distribution = config.get('distribution')

        if delay is not None:
            kwargs['delay'] = int(delay)
        if variation is not None:
            kwargs['variation'] = int(variation)
        if sigma is not None:
            kwargs['sigma'] = int(sigma)
        if distribution is not None:
            kwargs['distribution'] = str(distribution)
        

        return LatencyInjectorSpanListener(**kwargs)
            

        
