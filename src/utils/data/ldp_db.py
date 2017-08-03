import random, string

import requests
from rdflib import Dataset
from rdflib.term import Variable
from rdflib.plugins.sparql.results.jsonresults import JSONResult

from src.collections.models import *
from src.members.models import *
from src.service.models import Service
from src.utils.conversions.rda import RDATools, RDA
from src.utils.conversions.rdf import MappingTool
from src.utils.base.errors import NotFoundError, DBError, ForbiddenError, ParseError
from src.utils.ids.marmotta import Marmotta
from src.utils.ids.url_encoder import encoder
from src.utils.rdf.ldp import LDP
from src.utils.rdf.sparql import SPARQLTools
from .db import DBInterface

class LDPDataBase(DBInterface):
    """
    LDP Database class

    :param self: Object
    :type self: LDPDataBase
    :param server: Url of Marmotta server
    :type server: text

    :ivar marmotta: Marmotta object
    :ivar sparql: SPARQLTools object
    :ivar RDA: RDATools object
    """

    def __init__(self, server):
        self.marmotta = Marmotta(server)
        self.sparql = SPARQLTools(self.marmotta.sparql)
        self.RDA = MappingTool(RDA, RDATools)

    def ask_collection(self, c_id):
        if not isinstance(c_id, list):
            c_id = [c_id]
        ids = [self.marmotta.ldp(encoder.encode(id)) for id in c_id]
        result = self.sparql.find(ids,self.RDA.ns.Collection)
        return float(result.bindings.pop().get(Variable('size')))/len(c_id)

    def get_collection(self, c_id=None):
        # todo: ASK and check if collection exists
        if c_id is not None:
            result = self.sparql.select(self.marmotta.ldp(encoder.encode(c_id)))
            graph = result.toDataset().graph(self.marmotta.ldp(encoder.encode(c_id)))
            contents = self.RDA.graph_to_object(graph)
            if len(contents) is 0:
                raise NotFoundError()
        else:
            result = self.sparql.list(s=self.marmotta.ldp(),p=LDP.ns.contains)
            collections = [dct[Variable('o')] for dct in result.bindings]
            contents = []
            if len(collections):
                result = self.sparql.select(collections)
                ds = result.toDataset()
                graphs = [ds.graph(collection) for collection in collections]
                for graph in graphs:
                    contents += self.RDA.graph_to_object(graph)
        return contents

    def set_collection(self, c_obj, over_write=False):
        if isinstance(c_obj, Model):
            c_obj = [c_obj]
        elif not isinstance(c_obj, list):
            raise ParseError()
        # create LD collection and declare as ldp:BasicContainer
        ds = Dataset()
        ldp = ds.graph(identifier=LDP.ns)
        for c in c_obj:
            c_id = encoder.encode(c.id)
            collection = ds.graph(identifier=self.marmotta.ldp(c_id))
            collection += self.RDA.object_to_graph(collection.identifier, c)
            ldp += LDP.add_contains(self.marmotta.ldp(), collection.identifier)
            member = ds.graph(identifier=self.marmotta.ldp(c_id+'/member'))
            ldp += LDP.add_contains(collection.identifier, member.identifier)
        ins = self.sparql.insert(ds)
        if ins.status_code is 200:
            return c_obj
        else:
            raise DBError()

    def del_collection(self, c_id):
        if self.sparql.ask(self.marmotta.ldp(encoder.encode(c_id)), self.RDA.ns.Collection).askAnswer:
            self.sparql.delete(self.marmotta.ldp(encoder.encode(c_id)))
            return True
        else:
            raise NotFoundError()

    def upd_collection(self, c_obj):
        obj = self.get_collection(c_obj.id)
        if obj and obj.pop().capabilities.metadataIsMutable:
            self.del_collection(c_obj.id)
            self.set_collection(c_obj)
            return c_obj
        else:
            raise ForbiddenError()



    def get_member(self, c_id, m_id=None):
        # todo: ASK and check if member exists
        if m_id is not None:
            if not isinstance(m_id, list):
                m_id = [m_id]
            members = [self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(id)) for id in m_id]
            # ds = self.sparql.select(ids).toDataset()
            # contents = [self.RDA.graph_to_member(ds.graph(id)) for id in ids]
        else:
            id = self.marmotta.ldp(encoder.encode(c_id))
            if not self.sparql.ask(id, self.RDA.ns.Collection).askAnswer:
                raise NotFoundError
            lst = self.sparql.list(s=self.marmotta.ldp(encoder.encode(c_id)+"/member"), p=LDP.ns.contains)
            members = [dct[Variable('o')] for dct in lst.bindings]
        contents=[]
        if len(members):
            dataset = self.sparql.select(members).toDataset()
            graphs = [dataset.graph(member) for member in members]
            for graph in graphs:
                contents += self.RDA.graph_to_object(graph)
        if m_id is not None and len(contents) is 0:
            raise NotFoundError()
        return contents

    def set_member(self, c_id, m_obj):
        if isinstance(m_obj, Model):
            m_obj = [m_obj]
        elif not isinstance(m_obj, list):
            raise ParseError()

        c_ldp_id = self.marmotta.ldp(encoder.encode(c_id))
        collection = self.get_collection(c_id).pop() # 404 if collection not found

        if len(set([m.id for m in m_obj])) is not len(m_obj):
            raise ForbiddenError()
        if not collection.capabilities.membershipIsMutable:
            raise ForbiddenError()
        if collection.capabilities.restrictedToType:
            for m in m_obj:
                if not(hasattr(m,"datatype") and m.datatype in collection.capabilities.restrictedToType):
                    raise ForbiddenError()
        if collection.capabilities.maxLength >= 0:
            size = self.sparql.size(c_ldp_id).bindings.pop().get(Variable('size'))
            if int(size) > collection.capabilities.maxLength-len(m_obj):
                raise ForbiddenError()#"Operation forbidden. Collection of maximum size {} is full.".format(collection.capabilities.maxLength))

        ds = Dataset()
        ldp = ds.graph(identifier=LDP.ns)
        for m in m_obj:
            m_id = self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m.id))
            member = ds.graph(identifier=m_id)
            member += self.RDA.object_to_graph(member.identifier,m)
            ldp += LDP.add_contains(c_ldp_id+"/member",m_id,False)
        res = self.sparql.insert(ds)
        if res.status_code is not 200:
            raise DBError()
        return m_obj

    def del_member(self, c_id, m_id):
        collection = self.get_collection(c_id).pop() # 404 if collection not found
        if not collection.capabilities.membershipIsMutable:
            raise ForbiddenError()
        id = self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m_id))
        if self.sparql.ask(id, self.RDA.ns.Member).askAnswer:
            self.sparql.delete(id)
            return True
        else:
            raise NotFoundError()

    def upd_member(self, c_id, m_obj):
        # todo: needs a rewrite to be able to update when !membershipIsMutable
        self.del_member(c_id, m_obj.id)
        self.set_member(c_id, m_obj)
        return m_obj

    def ask_member(self, c_id, m_id):
        if not isinstance(m_id, list):
            m_id = [m_id]
        ids = [self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m)) for m in m_id]
        result = self.sparql.find(ids,self.RDA.ns.Member)
        return float(result.bindings.pop().get(Variable('size')))/len(m_id)



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
            s_obj = self.RDA.graph_to_object(ds.graph(id))
            return s_obj.pop()
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
        service += self.RDA.object_to_graph(service.identifier, s_obj)
        ldp = ds.graph(identifier=LDP.ns)
        ldp += LDP.add_contains(self.marmotta.ldp(),service.identifier,False)
        response = self.sparql.insert(ds)
        if response.status_code is 200:
            return s_obj
        else:
            raise DBError()



    def get_id(self, type_class):
        id = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))
        if type_class is CollectionObject:
            id = "urn:cite:test_collections."+id
        if type_class is MemberItem:
            id = "urn:cite:test_members."+id
        return id
