from rdflib import Literal, URIRef, Namespace, Graph
from rdflib.namespace import DCTERMS, RDF
from .struct import Struct
from .url_encoder import encoder
from .ldp import LDP
from src.members.models import MemberItem
from src.collections.models import *
from src.service.models import Service

boolean = lambda x: True if str(x)=='true' else False

def invert(dct):
    return {v['label']: {'label':k, 'type':v['type'], 'rdf': v['rdf'], 'map':invert(v['map'])} for k,v in dct.items() if not k.startswith("__")}

class RDATools:

    def __init__(self, marmotta):
        self.marmotta = marmotta
        self.ns = Namespace("http://rd-alliance.org/ns/collections#")
        # todo: consider merging everything into a single k-v-store?
        # todo: for that we would need to find alternative to iterating over maps in graph_to_dict()
        self.properties = {
            'CollectionObject': {
                str(DCTERMS.identifier): {'label': 'id', 'type': str, 'rdf': Literal, 'map': {}},
                str(DCTERMS.description): {'label': 'description', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#description"), 'map': {}},
                str(self.ns.hasCapabilities): {'label': 'capabilities', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#capabilities"), 'map': {
                    str(self.ns.isOrdered): {'label': 'isOrdered', 'type': boolean, 'rdf': Literal, 'map': {}},
                    str(self.ns.appendsToEnd): {'label': 'appendsToEnd', 'type': boolean, 'rdf': Literal, 'map': {}},
                    str(self.ns.maxLength): {'label': 'maxLength', 'type': int, 'rdf': Literal, 'map': {}},
                    str(self.ns.membershipIsMutable): {'label': 'membershipIsMutable', 'type': boolean, 'rdf': Literal, 'map': {}},
                    str(self.ns.metadataIsMutable): {'label': 'metadataIsMutable', 'type': boolean, 'rdf': Literal, 'map': {}},
                    str(self.ns.restrictedToType): {'label': 'restrictedToType', 'type': str, 'rdf': Literal, 'map': {}},
                    str(self.ns.supportsRoles): {'label': 'supportsRoles', 'type': boolean, 'rdf': Literal, 'map': {}},
                }},  # todo: fix URIs
                str(self.ns.hasProperties): {'label': 'properties', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#properties"), 'map': {
                    str(self.ns.modelType): {'label': 'modelType', 'type': str, 'rdf': URIRef, 'map': {}},
                    str(self.ns.descriptionOntology): {'label': 'descriptionOntology', 'type': str, 'rdf': URIRef, 'map': {}},
                    str(self.ns.memberOf): {'label': 'memberOf', 'type': str, 'rdf': URIRef, 'map': {}},
                    str(DCTERMS.license): {'label': 'license', 'type': str, 'rdf': Literal, 'map': {}},
                    str(DCTERMS.rightsHolder): {'label': 'ownership', 'type': str, 'rdf': Literal, 'map': {}},
                    str(self.ns.hasAccessRestrictions): {'label': 'hasAccessRestrictions', 'type': boolean, 'rdf': Literal, 'map': {}}
                }}
            },
            'MemberItem': {
                str(DCTERMS.identifier): {'label': 'id', 'type': str, 'rdf': Literal, 'map': {}},
                str(self.ns.location): {'label': 'location', 'type': str, 'rdf': Literal, 'map': {}},
                str(self.ns.datatype): {'label': 'datatype', 'type': str, 'rdf': Literal, 'map': {}},
                str(self.ns.ontology): {'label': 'ontology', 'type': str, 'rdf': Literal, 'map': {}},
                str(self.ns.mappings): {'label': 'mappings', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+'#mappings'), 'map': {
                    str(self.ns.role): {'label': 'role', 'type': str, 'rdf': Literal, 'map': {}},
                    str(self.ns.index): {'label': 'index', 'type': int, 'rdf': Literal, 'map': {}},
                    str(self.ns.dateAdded): {'label': 'dateAdded', 'type': str, 'rdf': Literal, 'map': {}}
                }}
            },
            'ServiceFeatures': {
                str(self.ns.providesCollectionPids): {'label': 'providesCollectionPids', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.collectionPidProviderType): {'label': 'collectionPidProviderType', 'type': str, 'rdf': Literal, 'map': {}}, # todo: URIRef?
                str(self.ns.enforcesAccess): {'label': 'enforcesAccess', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.supportsPagination): {'label': 'supportsPagination', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.asynchronousActions): {'label': 'asynchronousActions', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.ruleBasedGeneration): {'label': 'ruleBasedGeneration', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.maxExpansionDepth): {'label': 'maxExpansionDepth', 'type': int, 'rdf': Literal, 'map': {}},
                str(self.ns.providesVersioning): {'label': 'providesVersioning', 'type': boolean, 'rdf': Literal, 'map': {}},
                str(self.ns.supportedCollectionOperations): {'label': 'supportedCollectionOperations', 'type': str, 'rdf': Literal, 'map': {}},
                str(self.ns.supportedModelTypes): {'label': 'supportedModelTypes', 'type': str, 'rdf': URIRef, 'map': {}}
            }
        }
        # todo: fix
        self.inverted_properties = { key:invert(value) for key,value in self.properties.items() if not key.startswith("__")}

    """
    Convert a graph to a dictionary
    :parameter graph is the rdflib.Graph object which contains the whole graph
    :parameter node is the identifier for the object to be extracted as dictionary
    :parameter propertiesMap contain the conversion rules
    """
    def graph_to_dict(self, graph, node, propertiesMap):
        subnodes = set(s for s in graph.subjects() if s != node)
        dct = {}
        print("STATE: ", subnodes, node)
        for (prd, obj) in graph.predicate_objects(node):
            if obj in subnodes:
                key = propertiesMap.get(str(prd),{'label':str(prd)}).get('label')
                dct.update({key: self.graph_to_dict(graph,obj,propertiesMap.get(str(prd),{'map':{}}).get('map'))})
            elif str(prd) in propertiesMap or propertiesMap == {}:
                print(str(prd))
                key = propertiesMap.get(str(prd),{'label':str(prd)}).get('label')
                value = propertiesMap.get(str(prd),{'type':str}).get('type')(obj)
                #print(key, ": ", obj.n3(), " -> ", value)
                if not key in dct:
                    dct.update({key: value})
                else:
                    if isinstance(dct[key],list):
                        dct[key] = sorted(dct[key] + [value])
                    else:
                        dct[key] = sorted([dct[key],value])
        return dct

    """
    Convert a graph to a dictionary
    :parameter dict is the dictionary to be converted
    :parameter subject is the identifier for the object in the dictionary
    :parameter propertiesMap contain the conversion rules
    """
    def dict_to_graph(self, val, key=None, subject=None, map=None, g=Graph()):
        if isinstance(val, list) and key and subject:
            # note: if List then add items
            for item in val:
                self.dict_to_graph(item, key=key, subject=subject, map=map, g=g)
        elif isinstance(val, dict):
            if not subject:
                subject = g.identifier
            for k,v in [(k,v) for k,v in val.items() if not k.startswith("__")]:
                if isinstance(v, list):
                    self.dict_to_graph(v, key=k, subject=subject, map=map, g=g) # same subject, map
                elif isinstance(v, dict):
                    object = map.get(k,{'rdf':lambda x: x})['rdf'](subject)
                    g.add((subject, URIRef(map.get(k, {'label':k})['label']), object)) # same subject, map, obj w/ subject
                    self.dict_to_graph(v,key=k,subject=object,map=map.get(k,{'map':{}})['map'], g=g), # subject changed, map changed
                else:
                    obj = map.get(key,{'rdf': lambda x: URIRef(x) if str(x).startswith("http://") else Literal(x)})['rdf'](v)
                    g.add((subject, URIRef(map.get(k, {'label':k})['label']), obj)) # same subject,
        else:
            # note: if simple type then add to graph
            prop = URIRef(map.get(key, {'label': str(key)})['label']) # same subject, map
            obj = map.get(key,{'rdf': lambda x: URIRef(x) if str(x).startswith("http://") else Literal(x)})['rdf'](val)
            g.add((subject, prop, obj))
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