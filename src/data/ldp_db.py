import base64
import requests
from rdflib import Graph, Namespace, URIRef, Literal
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

    def get_collection(self, id:None):
        # todo: Graph() is a placeholder and needs to be replaced with the actual backend (either use SPARQLStore or raw requests.post)
        if id is not None:
            contents = [self.graph_to_collection(Graph().parse(self.ldp(self.b64encode(id))))]
        else:
            contents = [self.graph_to_collection(Graph().parse(str(collection))) for collection in Graph().parse(self.root).objects(None, LDP.contains)]
        return CollectionResultSet(contents)

    '''
        This is almost ready.
    '''
    def set_collection(self, c_obj):
        collection = self.collection_to_graph(c_obj)
        # todo: add rdf:types (BasicContainer, RDACollection)
        collection.add((URIRef(''), RDF.type, LDP.BasicContainer))
        # todo: response1 = POST to self.root
        response = requests.post(self.root, data=collection.serialize(format="turtle"), headers={'Content-Type':'text/turtle','Link':'<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"','Slug':self.b64encode(c_obj.id)})
        if response.status_code is 201:
            # todo: response2 = POST basiccontainer to self.root+c_obj.id+/members
            member = Graph()
            member.add((URIRef(''), RDF.type, LDP.BasicContainer))
            loc = response.headers.get('Location')
            requests.post(loc, data=member.serialize(format="turtle"), headers={'Content-Type':'text/turtle','Link':'<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"','Slug':'member'})
        else:
            raise KeyError
        # todo: return c_obj
        return c_obj

    def del_collection(self, id):
        requests.delete(self.root+id)
        # todo: wrap into flask response
        assert False

    def get_member(self, cid, mid:None):
        # todo: write graph_to_member
        # todo: set up properties for MemberItem
        # todo: return MemberResultSet
        assert False

    def set_member(self, cid, m_obj):
        # todo: write member_to_graph
        # todo: serialize to turtle
        # todo: send to self.root+b64encode(cid)+members
        assert False

    def del_member(self, cid, mid):
        # todo: requests.delete(self.root+id)
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

    def member_to_graph(self, m_obj):
        m_graph = Graph()
        m_graph.add((URIRef(""), DCTERMS.identifier, URIRef(m_obj.id)))
        m_graph.add((URIRef(""), RDA.location, URIRef(m_obj.location)))
        return m_graph