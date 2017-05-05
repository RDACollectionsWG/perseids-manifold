import base64, random, string
import requests
from rdflib import Dataset, Variable
from rdflib.plugins.sparql.results.jsonresults import JSONResult
from .db import DBInterface
from src.collections.models import *
from src.members.models import *
from src.service.models import Service
from src.utils.ldp import LDP
from src.utils.sparql import SPARQLTools
from src.utils.marmotta import Marmotta
from src.utils.url_encoder import encoder
from src.utils.rda import RDATools

class LDPDataBase(DBInterface):

    def __init__(self, server):
        self.marmotta = Marmotta(server)
        self.sparql = SPARQLTools()
        self.RDA = RDATools(self.marmotta)

    def get_collection(self, id=None):
        # todo: ASK and check if collection exists
        if id is not None:
            result = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.collections.select(self.marmotta.ldp(encoder.encode(id))), headers={"Accept":"application/sparql-results+json"}).json())
            graph = self.sparql.result_to_dataset(result).graph(self.marmotta.ldp(encoder.encode(id)))
            contents = self.RDA.graph_to_collection(graph)
            if len(contents) is 0:
                raise KeyError
        else:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.list(s=self.marmotta.ldp(),p=LDP.ns.contains), headers={"Accept":"application/sparql-results+json"})
            collections = [dct[Variable('o')] for dct in JSONResult(response.json()).bindings]
            contents = []
            for collection in collections:
                result = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.collections.select(collection), headers={"Accept":"application/sparql-results+json"}).json())
                graph = self.sparql.result_to_dataset(result).graph(collection)
                contents += self.RDA.graph_to_collection(graph)
        return contents

    def set_collection(self, c_obj):
        # create LD collection and declare as ldp:BasicContainer
        c_id = encoder.encode(c_obj.id)
        ds = Dataset()
        ldp = ds.graph(identifier=LDP.ns)

        collection = ds.graph(identifier=self.marmotta.ldp(c_id))
        collection += self.RDA.collection_to_graph(c_obj)
        ldp += LDP.add_contains(self.marmotta.ldp(), collection.identifier)

        member = ds.graph(identifier=self.marmotta.ldp(c_id+'/member'))
        ldp += LDP.add_contains(collection.identifier, member.identifier)
        insert = self.sparql.collections.insert(ds)
        response = requests.post(self.marmotta.sparql.update, data=insert)
        if response.status_code is 200:
            return c_obj
        else:
            raise KeyError

    def del_collection(self, id):
        found = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.collections.ask(self.marmotta.ldp(encoder.encode(id))), headers={"Accept":"application/sparql-results+json"}).json()).askAnswer
        if found:
            delete =self.sparql.collections.delete(self.marmotta.ldp(encoder.encode(id)))
            response = requests.post(self.marmotta.sparql.update, data=delete)
            if response.status_code is 200:
                return True
        raise KeyError

    def update_collection(self, c_obj):
        self.del_collection(c_obj.id)
        self.set_collection(c_obj)
        return c_obj

    def get_member(self, cid, mid=None):
        # todo: ASK and check if member exists
        if mid is not None:
            id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(mid))
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.members.select(id), headers={"Accept":"application/sparql-results+json"})
            ds =self.sparql.result_to_dataset(JSONResult(response.json()))
            contents = self.RDA.graph_to_member(ds.graph(id))
            if len(contents) is 0:
                raise KeyError
        else:
            listed = self.sparql.collections.list(s=self.marmotta.ldp(encoder.encode(cid)+"/member"), p=LDP.ns.contains)
            response = requests.post(self.marmotta.sparql.select, data=listed, headers={"Accept":"application/sparql-results+json"})
            members = [dct[Variable('o')] for dct in JSONResult(response.json()).bindings]
            contents = []
            for member in members:
                result = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.members.select(member), headers={"Accept":"application/sparql-results+json"}).json())
                graph =self.sparql.result_to_dataset(result).graph(member)
                contents += self.RDA.graph_to_member(graph)
        return contents

    def set_member(self, cid, m_obj):
        c_id = self.marmotta.ldp(encoder.encode(cid))
        m_id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(m_obj.id))
        found = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.collections.ask(c_id), headers={"Accept":"application/sparql-results+json"}).json()).askAnswer
        ds = Dataset()
        member = ds.graph(identifier=m_id)
        member += self.RDA.member_to_graph(cid,m_obj)
        ldp = ds.graph(identifier=LDP.ns)
        ldp += LDP.add_contains(c_id+"/member",m_id,False)
        insert =self.sparql.members.insert(ds)
        response = requests.post(self.marmotta.sparql.update, data=insert)
        if response.status_code is 200:
            return m_obj
        else:
            raise KeyError

    def del_member(self, cid, mid):
        id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(mid))
        found = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.members.ask(id), headers={"Accept":"application/sparql-results+json"}).json()).askAnswer
        if found:
            delete = self.sparql.collections.delete(id)
            response = requests.post(self.marmotta.sparql.update, data=delete)
            if response.status_code is 200:
                return True
        raise KeyError

    def update_member(self, cid, m_obj):
        self.del_member(cid, m_obj.id)
        self.set_member(cid, m_obj)
        return m_obj

    def get_service(self):
        id = self.marmotta.ldp("service")
        found = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.service.ask(id), headers={"Accept":"application/sparql-results+json"}).json()).askAnswer
        if found:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.service.select(id), headers={"Accept":"application/sparql-results+json"})
            ds =self.sparql.result_to_dataset(JSONResult(response.json()))
            s_obj =self.RDA.graph_to_service(ds.graph(id))
            return s_obj
        else:
            return Service()

    def set_service(self, s_obj):
        ds = Dataset()
        service = ds.graph(identifier=self.marmotta.ldp("service"))
        service += self.RDA.service_to_graph(s_obj)
        ldp = ds.graph(identifier=LDP.ns)
        ldp += LDP.add_contains(self.marmotta.ldp(),service.identifier,False)
        insert = self.sparql.service.insert(ds)
        response = requests.post(self.marmotta.sparql.update, data=insert)
        if response.status_code is 200:
            return s_obj
        else:
            raise IOError
    
    def get_id(self, type):
        id = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))
        if type is CollectionObject:
            id = "urn:cite:test_collections."+id
        if type is MemberItem:
            id = "urn:cite:test_members."+id
        return id