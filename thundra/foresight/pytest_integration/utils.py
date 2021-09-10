import wrapt

"""
    Refactor this file. It's been written rapidly.
"""


def _wrapper_setup_fixture(wrapped, instance, args, kwargs):
    res = None
    try:
        request = args[1]
        if not "x_thundra" in request.fixturename:
            print("before fixture call")
            res = wrapped(*args, **kwargs)
            print("after fixture call")
        else:
            res = wrapped(*args, **kwargs)
    except Exception as err:
        print("error occured while fixture_setup function wrapped") # TODO
        res = wrapped(*args, **kwargs)
    if res:
        return res


def _wrapper_teardown_fixture(wrapped, instance, args, kwargs):
    try:
        if not "x_thundra" in kwargs["request"].fixturename:
            print("before teardown function")
            wrapped(*args, **kwargs)
            print("after teardown function")
        else:
            wrapped(*args, **kwargs)
    except Exception as err:
        print("error occured while fixture_teardown function wrapped") # TODO
        wrapped(*args, **kwargs)


def patch():
    '''
        fixture function has been called in call_fixture_func.
    '''
    wrapt.wrap_function_wrapper(
            "_pytest.fixtures",
            "call_fixture_func",
            _wrapper_setup_fixture
        )
    '''
        teardown functions has been stored in a stack(FixtureDef._finalizer).
        finish function has been iterated over this stack and call teardown fixtures.
    '''    
    wrapt.wrap_function_wrapper(
            "_pytest.fixtures",
            "FixtureDef.finish",
            _wrapper_teardown_fixture
        )


def unpatch():
    pass #TODO