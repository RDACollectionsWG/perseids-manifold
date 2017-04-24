import base64
import requests
from datetime import datetime
from rdflib import Dataset, Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, DCTERMS
from .db import DBInterface
from src.collections.models import *
from src.members.models import *

LDP = Namespace("http://www.w3.org/ns/ldp#")
RDA = Namespace("http://rd-alliance.org/ns/collections#")

properties = {
    'CollectionObject': {
        str(DCTERMS.identifier): ['id', str, Literal],
        str(DCTERMS.description): ['description', str, Literal],
        str(RDA.hasCapabilities): ['capabilities', lambda x: x, lambda x: URIRef("#capabilities")],
        str(RDA.hasProperties): ['properties', lambda x: x, lambda x: URIRef("#properties")]
    },
    'CollectionCapabilities': {
        str(RDA.isOrdered): ['isOrdered', bool, Literal],
        str(RDA.appendsToEnd): ['appendsToEnd', bool, Literal],
        str(RDA.maxLength): ['maxLength', int, Literal],
        str(RDA.membershipIsMutable): ['membershipIsMutable', bool, Literal],
        str(RDA.metadataIsMutable): ['metadataIsMutable', bool, Literal],
        str(RDA.restrictedToType): ['restrictedToType', bool, Literal],
        str(RDA.supportsRole): ['supportsRoles', bool, Literal],
    },
    'CollectionProperties': {
        str(RDA.modelType): ['modelType', str, URIRef],
        str(RDA.descriptionOntology): ['descriptionOntology', str, URIRef],
        str(DCTERMS.license): ['license', str, URIRef],
        str(DCTERMS.rightsHolder): ['ownership', str, Literal],
        str(RDA.hasAccessRestrictions): ['hasAccessRestrictions', bool, Literal]
    }
}

inverted_properties = { key:{v[0]: [k,v[1],v[2]] for k,v in value.items() if not k.startswith("__")} for key,value in properties.items() if not key.startswith("__")}

class LDPDataBase(DBInterface):

    def __init__(self, server):
        server = Namespace(server) if server.endswith("/") else Namespace(server+"/")
        self.ldp = lambda slug=None: server.ldp if slug is None else server["ldp"+slug[:-1]] if slug.startswith("/") and slug.endswith("/") else server["ldp"+slug] if slug.startswith("/") else server["ldp/"+slug[:-1]] if slug.endswith("/") else server["ldp/"+slug]
        self.sparql = Struct(select=server["sparql/select"], update=server["sparql/update"])

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
        assert False
        
    def set_service(self, s_obj):
        assert False
    
    def get_id(self, type):
        assert False

    def b64encode(self, s):
        return base64.b64encode(str.encode(s)).decode()

    def b64decode(self, s):
        return base64.b64decode(s).decode()

    def graph_to_collection(self, g):
        containers = [self.graph_to_dict(g, sbj, properties['CollectionObject']) for sbj in g.subjects(RDF.type, LDP.Container)]
        for c in containers:
            c['capabilities'] = self.graph_to_dict(g, c['capabilities'], properties['CollectionCapabilities'])
            c['properties'] = self.graph_to_dict(g, c['properties'], properties['CollectionProperties'])
        return [CollectionObject(**c) for c in containers]

    '''
        Convert a collection object into a set of triples,
        using Base64 encoding for URL conformant IDs and
        #capabilities and #properties fragments
    '''
    def collection_to_graph(self,c_obj):
        node = self.ldp(self.b64encode(c_obj.id))
        capabilities = self.ldp(self.b64encode(c_obj.id)+'#capabilities')
        properties = self.ldp(self.b64encode(c_obj.id)+'#properties')
        g = Graph(identifier=node)
        g.add((node,RDF.type, RDA.Collection))
        return g + self.dict_to_graph(node, c_obj.dict(), inverted_properties['CollectionObject']) +\
               self.dict_to_graph(capabilities, c_obj.capabilities.dict(), inverted_properties['CollectionCapabilities']) +\
               self.dict_to_graph(properties, c_obj.properties.dict(), inverted_properties['CollectionProperties'])

    def graph_to_dict(self, graph, node, propertiesMap):
        return {propertiesMap[str(prd)][0]: propertiesMap[str(prd)][1](obj) for (prd, obj) in graph.predicate_objects(node) if str(prd) in propertiesMap}

    def dict_to_graph(self, subject, dict, propertiesMap):
        g = Graph()
        for k,v in dict.items():
            if not k.startswith("__"):
                g.add((subject, URIRef(propertiesMap[k][0]), propertiesMap[k][2](v)))
        return g

    def graph_to_member(self,g):
        return MemberItem()
        assert False

    def member_to_graph(self, c_id, m_obj):
        ldp_uri = self.ldp(self.b64encode(c_id)+"/member/"+self.b64encode(m_obj))
        m_graph = Graph()
        m_graph.add((ldp_uri, DCTERMS.identifier, URIRef(m_obj.id)))
        m_graph.add((ldp_uri, RDA.location, URIRef(m_obj.location)))
        return m_graph