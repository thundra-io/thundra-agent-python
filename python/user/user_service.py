import re
from random import randint

from thundra.plugins.trace.traceable import Traceable

from user.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    @Traceable(trace_args=True, trace_return_value=True)
    def save_user(self, name, surname, id):
        index = randint(10,20)
        try:
            validated = self._validate_id(id)
        except Exception as e:
            raise e
        if validated is True:
            return self.user_repository.save_user(index, name, surname, id)

    @Traceable(trace_args=True, trace_return_value=True)
    def get_user(self, index):
        return self.user_repository.find_user(index)


    @Traceable(trace_args=True, trace_return_value=True)
    def _validate_id(id):
        if re.match('([0-9]+)+[a-zA-Z]+', id):
            raise Exception('User id cannot start with number')
        return True