import base64
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
        str(DCTERMS.rightsHolder): ['owner', str, Literal],
        str(RDA.hasAccessRestrictions): ['hasAccessRestrictions', bool, Literal]
    }
}

class LDPDataBase(DBInterface):

    def __init__(self, root):
        self.root = root if root.endswith("/") else root+"/"

    def get_collection(self, id:None):
        if id is not None:
            contents = [self.graph_to_collection(Graph().parse(self.root+self.b64encode(id)))]
        else:
            contents = [self.graph_to_collection(Graph().parse(str(collection))) for collection in Graph().parse(self.root).objects(None, LDP.contains)]
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

    def graph_to_collection(self, g):
        containers = [self.graph_to_dict(g, sbj, properties['CollectionObject']) for sbj in g.subjects(RDF.type, LDP.Container)]
        for c in containers:
            c['capabilities'] = self.graph_to_dict(g, c['capabilities'], properties['CollectionCapabilities'])
            c['properties'] = self.graph_to_dict(g, c['properties'], properties['CollectionProperties'])
        return [CollectionObject(**c) for c in containers]

    def collection_to_graph(self,c_obj):
        node = URIRef(self.root+self.b64encode(c_obj.id))
        capabilities = URIRef(str(node)+'#capabilities')
        properties = URIRef(str(node)+'#properties')
        g = Graph()
        g.add((node, DCTERMS.identifier, Literal(c_obj.id)))
        assert False

    def graph_to_dict(self, graph, node, propertiesMap):
        return {propertiesMap[str(prd)][0]: propertiesMap[str(prd)][1](obj) for (prd, obj) in graph.predicate_objects(node) if str(prd) in propertiesMap}