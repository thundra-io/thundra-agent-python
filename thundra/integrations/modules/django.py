import wrapt

try:
    from django.conf import settings
except ImportError:
    settings = None

THUNDRA_MIDDLEWARE = "thundra.wrappers.django.middleware.ThundraMiddleware"


def _wrapper(wrapped, instance, args, kwargs):
    try:
        if getattr(settings, 'MIDDLEWARE', None):
            if THUNDRA_MIDDLEWARE in settings.MIDDLEWARE:
                return wrapped(*args, **kwargs)

            if isinstance(settings.MIDDLEWARE, tuple):
                settings.MIDDLEWARE = (THUNDRA_MIDDLEWARE,) + settings.MIDDLEWARE
            elif isinstance(settings.MIDDLEWARE, list):
                settings.MIDDLEWARE = [THUNDRA_MIDDLEWARE] + settings.MIDDLEWARE
        elif getattr(settings, 'MIDDLEWARE_CLASSES', None):
            if THUNDRA_MIDDLEWARE in settings.MIDDLEWARE_CLASSES:
                return wrapped(*args, **kwargs)

            if isinstance(settings.MIDDLEWARE_CLASSES, tuple):
                settings.MIDDLEWARE = (THUNDRA_MIDDLEWARE,) + settings.MIDDLEWARE_CLASSES
            elif isinstance(settings.MIDDLEWARE_CLASSES, list):
                settings.MIDDLEWARE = [THUNDRA_MIDDLEWARE] + settings.MIDDLEWARE_CLASSES

    except Exception:
        pass
    return wrapped(*args, **kwargs)


def patch():
    pass
    """
    wrapt.wrap_function_wrapper(
        'django.core.handlers.base',
        'BaseHandler.load_middleware',
        _wrapper
    )
    """
