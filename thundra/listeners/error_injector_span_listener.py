from __future__ import absolute_import
import builtins
import logging
from threading import Lock
from importlib import import_module
from thundra import constants, utils
from thundra.listeners.thundra_span_listener import ThundraSpanListener

logger = logging.getLogger(__name__)
default_error_message = "Error injected by Thundra!"
default_error_type = Exception

class ErrorInjectorSpanListener(ThundraSpanListener):
    def __init__(self, error_message=default_error_message, 
        error_type=default_error_type, inject_on_finish=False,
        inject_count_freq=1, add_info_tags=True):

        self._counter = 0
        self._lock = Lock()

        self.error_message = error_message
        self.error_type = error_type
        self.inject_on_finish = inject_on_finish
        self.inject_count_freq = max(inject_count_freq, 1)
        self.add_info_tags = add_info_tags
    
    def on_span_started(self, span):
        if (not self.inject_on_finish
            and self._able_to_raise()):
            self._raise_error(span)

    def on_span_finished(self, span):
        if (self.inject_on_finish
            and self._able_to_raise()):
            self._raise_error(span)

    def _raise_error(self, span):
        err = self.error_type(self.error_message)
        if self.add_info_tags:
            self._add_info_tags(span)
        raise err
    
    def _able_to_raise(self):
        if self._increment_and_get_counter() % self.inject_count_freq == 0:
            return True
        return False

    def _increment_and_get_counter(self):
        with self._lock:
            self._counter += 1
        
        return self._counter
    
    def _add_info_tags(self, span):
        try:
            info_dict = {
                'type': 'error_injector_span_listener',
                'error_type': str(self.error_type),
                'error_message': self.error_message,
                'inject_on_finish': self.inject_on_finish,
                'inject_count_freq': self.inject_count_freq,
            }
            span.set_tag(constants.THUNDRA_LAMBDA_SPAN_LISTENER_INFO_TAG, info_dict)
        except Exception as e:
            logger.error("error while adding ErrorInjectorSpanListener info tags: %s", e)
    
    @staticmethod
    def from_config(config):
        kwargs = {}
        error_message = config.get('errorMessage')
        error_type = config.get('errorType')
        inject_on_finish = config.get('injectOnFinish')
        inject_count_freq = config.get('injectCountFreq')
        add_info_tags = config.get('addInfoTags')

        if error_message is not None:
            try:
                kwargs['error_message'] = error_message.strip('"')
            except AttributeError:
                ErrorInjectorSpanListener._log_value_parse_err(error_message, 'error_message')
        if error_type is not None:
            if hasattr(builtins, error_type):
                err_class = getattr(builtins, error_type)
                if issubclass(err_class, BaseException):
                    kwargs['error_type'] = getattr(builtins, error_type)
            else:
                try:
                    (err_module_name, err_class_name) = error_type.rsplit('.', 1)
                    err_module = import_module(err_module_name)
                    if hasattr(err_module, err_class_name):
                        err_class = getattr(err_module, err_class_name)
                        if issubclass(err_class, BaseException):
                            kwargs['error_type'] = err_class
                except (ImportError, ValueError):
                    logger.error("couldn't import %s", error_type)
        if inject_on_finish is not None:
            try:
                kwargs['inject_on_finish'] = utils.str2bool(inject_on_finish)
            except ValueError:
                ErrorInjectorSpanListener._log_value_parse_err(inject_on_finish, 'inject_on_finish')
        if inject_count_freq is not None:
            try:
                kwargs['inject_count_freq'] = int(inject_count_freq)
            except ValueError:
                ErrorInjectorSpanListener._log_value_parse_err(inject_count_freq, 'inject_count_freq')
        if add_info_tags is not None:
            try:
                kwargs['add_info_tags'] = utils.str2bool(add_info_tags)
            except ValueError:
                ErrorInjectorSpanListener._log_value_parse_err(add_info_tags, 'add_info_tags')

        return ErrorInjectorSpanListener(**kwargs)

    @staticmethod
    def _log_value_parse_err(param, param_name):
        logger.error(("couldn't parse %s parameter (%s) of "
            "ErrorInjectorSpanListener, using the default value"), param_name, param)

    @staticmethod
    def should_raise_exceptions():
        return True
