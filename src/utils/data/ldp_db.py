import random, string, time

import requests
from rdflib import Dataset, Variable
from rdflib.plugins.sparql.results.jsonresults import JSONResult

from src.collections.models import *
from src.members.models import *
from src.service.models import Service
from src.utils.conversions.rda import RDATools
from src.utils.base.errors import NotFoundError, DBError, ForbiddenError
from src.utils.ids.marmotta import Marmotta
from src.utils.ids.url_encoder import encoder
from src.utils.rdf.ldp import LDP
from src.utils.rdf.sparql import SPARQLTools
from .db import DBInterface

profiling = False

class LDPDataBase(DBInterface):

    def __init__(self, server):
        self.marmotta = Marmotta(server)
        self.sparql = SPARQLTools()
        self.RDA = RDATools(self.marmotta)

    def get_collection(self, id=None):
        # todo: ASK and check if collection exists
        if id is not None:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.select(self.marmotta.ldp(encoder.encode(id))), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            if response.status_code is not 200:
                raise DBError()
            result = JSONResult(response.json())
            graph = self.sparql.result_to_dataset(result).graph(self.marmotta.ldp(encoder.encode(id)))
            contents = self.RDA.graph_to_collection(graph)
            if len(contents) is 0:
                raise NotFoundError()
        else:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.list(s=self.marmotta.ldp(),p=LDP.ns.contains), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            if response.status_code is not 200:
                raise DBError()
            collections = [dct[Variable('o')] for dct in JSONResult(response.json()).bindings]
            contents = []
            if len(collections):
                response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.selects(collections), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
                if response.status_code is not 200:
                    raise DBError()
                result = JSONResult(response.json())
                graphs = [self.sparql.result_to_dataset(result).graph(collection) for collection in collections]
                for graph in graphs:
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
        response = requests.post(self.marmotta.sparql.update, data=insert, headers={"Content-Type":"application/sparql-update; charset=utf-8"})
        if response.status_code is 200:
            return c_obj
        else:
            raise DBError()

    def del_collection(self, id):
        found = JSONResult(requests.post(self.marmotta.sparql.select, data=self.sparql.collections.ask(self.marmotta.ldp(encoder.encode(id))), headers={"Accept":"application/sparql-results+json","Content-Type":"application/sparql-select"}).json()).askAnswer
        if found:
            delete =self.sparql.collections.delete(self.marmotta.ldp(encoder.encode(id)))
            response = requests.post(self.marmotta.sparql.update, data=delete)
            if response.status_code is 200:
                return True
            else:
                raise DBError()
        else:
            raise NotFoundError()

    def upd_collection(self, c_obj):
        self.del_collection(c_obj.id)
        self.set_collection(c_obj)
        return c_obj

    def get_member(self, cid, mid=None):
        # todo: ASK and check if member exists
        if mid is not None:
            id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(mid))
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.members.select(id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            if response.status_code is not 200:
                raise DBError()
            ds =self.sparql.result_to_dataset(JSONResult(response.json()))
            contents = self.RDA.graph_to_member(ds.graph(id))
            if len(contents) is 0:
                raise NotFoundError()
        else:
            tf = time.time()
            t1 = time.time()
            id = self.marmotta.ldp(encoder.encode(cid))
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.ask(id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            print("ASK COLLECTION: ", time.time()-t1) if profiling else ''
            t1 = time.time()
            if response.status_code is not 200:
                raise DBError()
            found = JSONResult(response.json()).askAnswer
            if not found:
                raise NotFoundError
            print("PARSE RESULT: ", time.time()-t1) if profiling else ''
            t1 = time.time()
            listed = self.sparql.collections.list(s=self.marmotta.ldp(encoder.encode(cid)+"/member"), p=LDP.ns.contains)
            response = requests.post(self.marmotta.sparql.select, data=listed, headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            print("GET MEMBER IDs: ", time.time()-t1) if profiling else ''
            t1 = time.time()
            if response.status_code is not 200:
                raise DBError()
            members = [dct[Variable('o')] for dct in JSONResult(response.json()).bindings]
            contents=[]
            if len(members):
                t1 = time.time()
                response = requests.post(self.marmotta.sparql.select, data=self.sparql.members.selects(members), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
                print("GET MEMBERS: ", time.time()-t1) if profiling else ''
                if response.status_code is not 200:
                    raise DBError()
                t1 = time.time()
                result = JSONResult(response.json())
                print("CONVERT RESULT: ", time.time()-t1) if profiling else ''
                t1 = time.time()
                dataset = self.sparql.result_to_dataset(result)
                print("CONVERT DATASET: ", time.time()-t1) if profiling else ''
                t1 = time.time()
                graphs = [dataset.graph(member) for member in members]
                print("CONVERT GRAPHS: ", time.time()-t1) if profiling else ''
                t1 = time.time()
                for graph in graphs:
                    contents += self.RDA.graph_to_member(graph)
                print("CONVERT CONTENTS: ", time.time()-t1) if profiling else ''
            print("TOTAL: ", time.time()-tf) if profiling else ''
        return contents

    def set_member(self, cid, m_obj):

        c_id = self.marmotta.ldp(encoder.encode(cid))
        m_id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(m_obj.id))
        collection = self.get_collection(cid).pop() # 404 if collection not found

        if not collection.capabilities.membershipIsMutable:
            raise ForbiddenError()


        if collection.capabilities.maxLength >= 0:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.collections.size(c_id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            if response.status_code is not 200:
                raise DBError()
            size = JSONResult(response.json()).bindings.pop().get(Variable('size'))
            if int(size) >= collection.capabilities.maxLength:
                raise ForbiddenError()#"Operation forbidden. Collection of maximum size {} is full.".format(collection.capabilities.maxLength))

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
            raise DBError()

    def del_member(self, cid, mid):
        collection = self.get_collection(cid).pop() # 404 if collection not found
        if not collection.capabilities.membershipIsMutable:
            raise ForbiddenError()
        
        id = self.marmotta.ldp(encoder.encode(cid)+"/member/"+encoder.encode(mid))
        response = requests.post(self.marmotta.sparql.select, data=self.sparql.members.ask(id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
        if response.status_code is not 200:
            raise DBError()
        found = JSONResult(response.json()).askAnswer
        if found:
            delete = self.sparql.collections.delete(id)
            response = requests.post(self.marmotta.sparql.update, data=delete)
            if response.status_code is 200:
                return True
            else:
                raise DBError()
        else:
            raise NotFoundError()

    def upd_member(self, cid, m_obj):
        self.del_member(cid, m_obj.id)
        self.set_member(cid, m_obj)
        return m_obj

    def get_service(self):
        id = self.marmotta.ldp("service")
        response = requests.post(self.marmotta.sparql.select, data=self.sparql.service.ask(id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
        if response.status_code is not 200:
            raise DBError()
        found = JSONResult(response.json()).askAnswer
        if found:
            response = requests.post(self.marmotta.sparql.select, data=self.sparql.service.select(id), headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            if response.status_code is not 200:
                raise DBError()
            ds =self.sparql.result_to_dataset(JSONResult(response.json()))
            s_obj =self.RDA.graph_to_service(ds.graph(id))
            return s_obj
        else:
            return Service(**{
                "providesCollectionPids": False,
                "collectionPidProviderType": False,
                "enforcesAccess": False,
                "supportsPagination": False,
                "asynchronousActions": False,
                "ruleBasedGeneration": False,
                "maxExpansionDepth": -1,
                "providesVersioning": False,
                "supportedCollectionOperations": [],
                "supportedModelTypes": []
            })

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
            raise DBError()
    
    def get_id(self, type):
        id = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))
        if type is CollectionObject:
            id = "urn:cite:test_collections."+id
        if type is MemberItem:
            id = "urn:cite:test_members."+id
        return id
