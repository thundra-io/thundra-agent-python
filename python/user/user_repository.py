from thundra.plugins.trace.traceable import Traceable

from user.user import User


class UserRepository:
    def __init__(self):
        self.users = {
            0: User("Frank", "Darabont", 'FD01021992'),
            1: User("Francis", "Coppola", 'FC02031972'),
            2: User("Christopher", "Nolan", 'CN03042008'),
            3: User("Ford", "Coppola", 'FC04051974'),
            4: User("Quentin", "Tarantino", 'QT06071994'),
            5: User("Steven", "Spielberg", 'SS06071993'),
            6: User("Peter", "Jackson", 'PJ07082003'),
            7: User("Sergio", "Leone", 'SL08091966'),
            8: User("Sidney", "Lumet", '09101957'),
            9: User("Robert", "Zemeckis", 'RZ10111994')
        }

    @Traceable(trace_args=True, trace_return_value=True)
    def save_user(self, index, name, surname, id):
        user = User(name, surname, id)
        self.users[index] = user
        return user


    @Traceable(trace_args=True, trace_return_value=True)
    def find_user(self, index):
        return self.users[index] if id in self.users else None