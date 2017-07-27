from .db import DBInterface


class NullDB(DBInterface):

    def ask_collection(self, c_id):
        return 0

    def ask_member(self, c_id, m_id):
        return 0

    def get_collection(self, c_id=None):
        return []

    def set_collection(self, c_obj):
        return c_obj

    def del_collection(self, c_id):
        return []

    def upd_collection(self, c_obj):
        return c_obj

    def get_member(self, c_id, m_id=None):
        return []

    def set_member(self, c_id, m_obj):
        return m_obj

    def del_member(self, c_id, m_id):
        return []

    def upd_member(self, c_id, m_obj):
        return m_obj

    def get_service(self):
        return []

    def set_service(self, s_obj):
        return s_obj

    def get_id(self, type_class):
        return ""