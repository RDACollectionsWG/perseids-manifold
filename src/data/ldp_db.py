import base64
from rdflib import Graph, Namespace
from .db import DBInterface
from src.collections.models import CollectionResultSet

ldp = Namespace("http://www.w3.org/ns/ldp#")

class LDPDataBase(DBInterface):

    def __init__(self, root):
        self.root = root if root.endswith("/") else root+"/"

    def get_collection(self, id:None):
        if id is not None:
            contents = [self.graph_to_collection(Graph().parse(self.root+self.b64encode(id)))]
        else:
            contents = [self.graph_to_collection(Graph().parse(str(collection))) for collection in Graph().parse(self.root).objects(None, ldp.contains)]
        return CollectionResultSet(contents)

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
