from thundra.listeners.aws_xray_listeners import AWSXRayListener


class AWSXRayListenerTesting(AWSXRayListener):
    def __init__(self):
        self.test_data = None
        super(AWSXRayListenerTesting, self).__init__()

    def _end_subsegment(self, span):
        if AWSXRayListener.xray_available():
            xray_recorder = AWSXRayListener.get_xray_recorder()
            self.test_data = {'xray': vars(xray_recorder.current_subsegment()), 'span': vars(span)}
        super(AWSXRayListenerTesting, self)._end_subsegment(span)
