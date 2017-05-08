from rdflib import Literal, URIRef, Namespace, Graph
from rdflib.namespace import DCTERMS, RDF
from .struct import Struct
from .url_encoder import encoder
from .ldp import LDP
from src.members.models import MemberItem
from src.collections.models import *
from src.service.models import Service

boolean = lambda x: True if str(x)=='true' else False

class RDATools:

    def __init__(self, marmotta):
        self.marmotta = marmotta
        self.ns = Namespace("http://rd-alliance.org/ns/collections#")
        self.properties = {
            'CollectionObject': {
                str(DCTERMS.identifier): ['id', str, Literal],
                str(DCTERMS.description): ['description', str, Literal],
                str(self.ns.hasCapabilities): ['capabilities', lambda x: x, lambda x: URIRef(x+"#capabilities")],  # todo: fix URIs
                str(self.ns.hasProperties): ['properties', lambda x: x, lambda x: URIRef(x+"#properties")]
            },
            'CollectionCapabilities': {
                str(self.ns.isOrdered): ['isOrdered', boolean, Literal],
                str(self.ns.appendsToEnd): ['appendsToEnd', boolean, Literal],
                str(self.ns.maxLength): ['maxLength', int, Literal],
                str(self.ns.membershipIsMutable): ['membershipIsMutable', boolean, Literal],
                str(self.ns.metadataIsMutable): ['metadataIsMutable', boolean, Literal],
                str(self.ns.restrictedToType): ['restrictedToType', str, Literal],
                str(self.ns.supportsRole): ['supportsRoles', boolean, Literal],
            },
            'CollectionProperties': {
                str(self.ns.modelType): ['modelType', str, URIRef],
                str(self.ns.descriptionOntology): ['descriptionOntology', str, URIRef],
                str(self.ns.memberOf): ['memberOf', str, URIRef],
                str(DCTERMS.license): ['license', str, Literal],
                str(DCTERMS.rightsHolder): ['ownership', str, Literal],
                str(self.ns.hasAccessRestrictions): ['hasAccessRestrictions', boolean, Literal]
            },
            'MemberItem': {
                str(DCTERMS.identifier): ['id', str, Literal],
                str(self.ns.location): ['location', str, Literal],
                str(self.ns.datatype): ['datatype', str, Literal],
                str(self.ns.ontology): ['ontology', str, Literal],
                str(self.ns.mappings): ['mappings', lambda x: x, lambda x: URIRef(x+'#mappings')]
            },
            'MemberItemMappings': {
                str(self.ns.role): ['role', str, Literal],
                str(self.ns.index): ['index', int, Literal],
                str(self.ns.dateAdded): ['dateAdded', str, Literal]
            },
            'ServiceFeatures': {
                str(self.ns.providesCollectionPids): ['providesCollectionPids', boolean, Literal],
                str(self.ns.collectionPidProviderType): ['collectionPidProviderType', str, Literal], # todo: URIRef?
                str(self.ns.enforcesAccess): ['enforcesAccess', boolean, Literal],
                str(self.ns.supportsPagination): ['supportsPagination', boolean, Literal],
                str(self.ns.asynchronousActions): ['asynchronousActions', boolean, Literal],
                str(self.ns.ruleBasedGeneration): ['ruleBasedGeneration', boolean, Literal],
                str(self.ns.maxExpansionDepth): ['maxExpansionDepth', int, Literal],
                str(self.ns.providesVersioning): ['providesVersioning', boolean, Literal],
                str(self.ns.supportedCollectionOperations): ['supportedCollectionOperations', str, Literal],
                str(self.ns.supportedModelTypes): ['supportedModelTypes', str, URIRef]
            }
        }
        self.inverted_properties = { key:{v[0]: [k,v[1],v[2]] for k,v in value.items() if not k.startswith("__")} for key,value in self.properties.items() if not key.startswith("__")}

    def graph_to_dict(self, graph, node, propertiesMap):
        dct = {}
        #print("\n")
        for (prd, obj) in graph.predicate_objects(node):
            if str(prd) in propertiesMap:
                key = propertiesMap[str(prd)][0]
                value = propertiesMap[str(prd)][1](obj)
                #print(key, ": ", obj.n3(), " -> ", value)
                if not key in dct:
                    dct.update({key: value})
                else:
                    if isinstance(dct[key],list):
                        dct[key] = sorted(dct[key] + [value])
                    else:
                        dct[key] = sorted([dct[key],value])
        return dct

    def dict_to_graph(self, subject, dict, propertiesMap):
        g = Graph()
        for k,v in dict.items():
            if not k.startswith("__"):
                if isinstance(v, list):
                    for w in v:
                        g.add((subject, URIRef(propertiesMap[k][0]), propertiesMap[k][2](w)))
                else:
                    if k in ["capabilities", "properties", "mappings"]:
                        g.add((subject, URIRef(propertiesMap[k][0]), propertiesMap[k][2](subject)))
                    else:
                        g.add((subject, URIRef(propertiesMap[k][0]), propertiesMap[k][2](v)))
        return g

    def graph_to_collection(self, g):
        containers = [self.graph_to_dict(g, sbj, self.properties['CollectionObject']) for sbj in g.subjects(RDF.type, self.ns.Collection)]
        for c in containers:
            c['capabilities'] = self.graph_to_dict(g, c['capabilities'], self.properties['CollectionCapabilities'])
            c['properties'] = self.graph_to_dict(g, c['properties'], self.properties['CollectionProperties'])
        return [CollectionObject(**c) for c in containers]

    '''
        Convert a collection object into a set of triples,
        using Base64 encoding for URL conformant IDs and
        #capabilities and #properties fragments
    '''
    def collection_to_graph(self,c_obj):
        node = self.marmotta.ldp(encoder.encode(c_obj.id))
        capabilities = self.marmotta.ldp(encoder.encode(c_obj.id)+'#capabilities')
        properties = self.marmotta.ldp(encoder.encode(c_obj.id)+'#properties')
        g = Graph(identifier=node)
        g.add((node,RDF.type, self.ns.Collection))
        # todo:
        g += (self.dict_to_graph(node, c_obj.dict(), self.inverted_properties['CollectionObject']) + \
              self.dict_to_graph(capabilities, c_obj.capabilities.dict(), self.inverted_properties['CollectionCapabilities']) + \
              self.dict_to_graph(properties, c_obj.properties.dict(), self.inverted_properties['CollectionProperties']))
        return g

    def graph_to_member(self,g):
        members = [self.graph_to_dict(g, sbj, self.properties['MemberItem']) for sbj in g.subjects(RDF.type, self.ns.Member)]
        for m in members:
            if m.get('mappings') is not None:
                # todo: probably allows for false positives
                m['mappings'] = self.graph_to_dict(g, m['mappings'], self.properties['MemberItemMappings'])
        return [MemberItem(**m) for m in members]

    def member_to_graph(self, c_id, m_obj):
        m_dict = m_obj.dict()
        node = self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m_obj.id))
        g = Graph(identifier=node)
        g.add((node, RDF.type, self.ns.Member))
        g += self.dict_to_graph(node, m_dict, self.inverted_properties['MemberItem'])
        if m_dict.get('mappings') is not None:
            mappings = self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m_obj.id)+"#mappings")
            g+=self.dict_to_graph(mappings, m_dict.get('mappings'), self.inverted_properties['MemberItemMappings'])
        return g

    def graph_to_service(self, g):
        services = [sbj for sbj in g.subjects(RDF.type, self.ns.Service)]
        if len(services) is 1:
            service = services.pop()
            return Service(**self.graph_to_dict(g, service, self.properties['ServiceFeatures']))
        else:
            raise KeyError

    def service_to_graph(self,s_obj):
        node = self.marmotta.ldp("service")
        g = Graph(identifier=node)
        g.add((node, RDF.type, self.ns.Service))
        g += self.dict_to_graph(node, s_obj.dict(), self.inverted_properties['ServiceFeatures'])
        return g