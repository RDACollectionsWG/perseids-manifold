import base64
from .db import DBInterface

class LDPDataBase(DBInterface):

    def __init__(self, root):
        self.root = root if root.endswith("/") else root+"/"

    def get_collection(self, id:None):
        assert False

    def set_collection(self, c_obj):
        assert False

    def del_collection(self, id):
        assert False

    def get_member(self, cid, mid:None):
        assert False

    def set_member(self, cid, m_obj):
        assert False

    def del_member(self, cid, mid):
        assert False

    def get_service(self):
        assert False
        
    def set_service(self, s_obj):
        assert False
    
    def get_id(self, type):
        assert False

    def b64encode(self, s):
        return base64.b64encode(str.encode(s)).decode()

    def b64decode(self, s):
        return base64.b64decode(s).decode()
