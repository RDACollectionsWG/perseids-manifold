import abc


class DBInterface(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_collection(self, id=None):
        pass

    @abc.abstractmethod
    def set_collection(self, c_obj):
        pass

    @abc.abstractmethod
    def del_collection(self, id):
        pass

    @abc.abstractmethod
    def upd_collection(self, c_obj):
        pass

    @abc.abstractmethod
    def get_member(self, id=None):
        pass

    @abc.abstractmethod
    def set_member(self, c_id, m_obj):
        pass

    @abc.abstractmethod
    def del_member(self, c_id, m_id):
        pass

    @abc.abstractmethod
    def upd_member(self, c_id, m_obj):
        pass

    @abc.abstractmethod
    def get_service(self):
        pass

    @abc.abstractmethod
    def set_service(self, s_obj):
        pass

    @abc.abstractmethod
    def get_id(self, type):
        pass
