import abc


class ACLInterface(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_permission(self, uID=None, cID=None, mID=None):
        pass

    @abc.abstractmethod
    def set_permission(self, p, uID=None, cID=None, mID=None):
        pass

    @abc.abstractmethod
    def get_user(self):
        pass
