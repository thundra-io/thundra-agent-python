import catchpoint.plugins.invocation.invocation_support as invocation_support


def test_set_get_tag():
    (key, value) = ('test_key', 'test_value')
    invocation_support.set_tag(key, value)

    assert invocation_support.get_tag(key) == value


def test_set_get_agent_tag():
    (key, value) = ('test_key', 'test_value')
    invocation_support.set_agent_tag(key, value)

    assert invocation_support.get_agent_tag(key) == value


def test_remove_tag():
    (key, value) = ('test_key', 'test_value')
    invocation_support.set_tag(key, value)
    invocation_support.remove_tag(key)
    assert invocation_support.get_tag(key) is None


def test_remove_agent_tag():
    (key, value) = ('test_key', 'test_value')
    invocation_support.set_agent_tag(key, value)
    invocation_support.remove_agent_tag(key)
    assert invocation_support.get_agent_tag(key) is None


def test_clear_tags():
    pairs = {
        'test_key_1': 'test_value_1',
        'test_key_2': 'test_value_2',
        'test_key_3': 'test_value_3',
    }
    invocation_support.set_many(pairs)
    invocation_support.clear()

    assert all([invocation_support.get_tag(key) is None for key in pairs])


def test_clear_agent_tags():
    pairs = {
        'test_key_1': 'test_value_1',
        'test_key_2': 'test_value_2',
        'test_key_3': 'test_value_3',
    }
    invocation_support.set_many_agent(pairs)
    invocation_support.clear()

    assert all([invocation_support.get_agent_tag(key) is None for key in pairs])


def test_set_error():
    e = Exception("test exception")
    invocation_support.set_error(e)

    assert invocation_support.get_error() == e
