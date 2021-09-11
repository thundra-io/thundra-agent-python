class TestRunnerScopeStore:
    """
        For pytest.request, use request.node
    """

    test_item_store_map = dict() # keeps <item.nodeid, ThundraScope>


    @staticmethod
    def get_item_id(item):
        return item.nodeid


    @classmethod
    def get(cls, item):
        item_id = item.nodeid
        return cls.test_item_store_map.get(item_id, None)


    @classmethod
    def add(cls, item, test_runner_scope):
        item_id = item.nodeid
        cls.test_item_store_map[item_id] = test_runner_scope


    @classmethod
    def remove(cls, item):
        item_id = item.nodeid
        return cls.test_item_store_map.pop(item_id, None)
