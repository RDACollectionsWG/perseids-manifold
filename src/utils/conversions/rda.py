from rdflib import Literal, URIRef, Namespace, Graph
from rdflib.namespace import DCTERMS, RDF

from src.collections.models import *
from src.members.models import MemberItem, CollectionItemMappingMetadata
from src.service.models import Service
from src.utils.ids.url_encoder import encoder

boolean = lambda x: True if str(x)=='true' else False

RDA = Namespace("http://rd-alliance.org/ns/collections#")

def invert(dct):
    return {v['label']: {'label':k, 'type':v['type'], 'rdf': v['rdf'], 'map':invert(v['map'])} for k,v in dct.items() if not k.startswith("__")}

class RDATools:

    def __init__(self, marmotta):
        self.marmotta = marmotta
        self.ns = RDA
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
                    str(self.ns.itemIndex): {'label': 'index', 'type': int, 'rdf': Literal, 'map': {}},
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
        for (prd, obj) in graph.predicate_objects(node):
            if obj in subnodes:
                key = propertiesMap.get(str(prd),{'label':str(prd).replace(str(node)+"@","")}).get('label')
                dct.update({key: self.graph_to_dict(graph,obj,propertiesMap.get(str(prd),{'map':{}}).get('map'))})
            elif obj == RDF.nil:
                key = propertiesMap.get(str(prd),{'label':str(prd).replace(str(node)+"@","")}).get('label')
                dct.update({key: []})
            elif str(prd) in propertiesMap or propertiesMap == {}:
                key = propertiesMap.get(str(prd),{'label':str(prd).replace(str(node)+"@","")}).get('label')
                value = propertiesMap.get(str(prd),{'type':str}).get('type')(obj)
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
            if len(val) is 0:
                g.add((subject,URIRef(map.get(key, {'label': str(subject)+"@"+str(key)})['label']), RDF.nil))
        elif isinstance(val, dict):
            if not subject:
                subject = g.identifier
            for k,v in [(k,v) for k,v in val.items() if not k.startswith("__")]:
                if isinstance(v, list):
                    self.dict_to_graph(v, key=k, subject=subject, map=map, g=g) # same subject, map
                elif isinstance(v, dict):
                    object = map.get(k,{'rdf':lambda x: x})['rdf'](subject)
                    g.add((subject, URIRef(map.get(k, {'label':str(subject)+"@"+k})['label']), object)) # same subject, map, obj w/ subject
                    self.dict_to_graph(v,key=k,subject=object,map=map.get(k,{'map':{}})['map'], g=g), # subject changed, map changed
                else:
                    obj = map.get(key,{'rdf': lambda x: URIRef(x) if str(x).startswith("http://") else Literal(x)})['rdf'](v)
                    g.add((subject, URIRef(map.get(k, {'label':str(subject)+"@"+k})['label']), obj)) # same subject,
        else:
            # note: if simple type then add to graph
            prop = URIRef(map.get(key, {'label': str(subject)+"@"+str(key)})['label']) # same subject, map
            obj = map.get(key,{'rdf': lambda x: URIRef(x) if str(x).startswith("http://") else Literal(x)})['rdf'](val)
            g.add((subject, prop, obj))
        return g

    def graph_to_collection(self, g):
        subjects = [s for s in g.subjects(RDF.type, self.ns.Collection)]
        for sbj in subjects:
            g.remove((sbj,RDF.type,self.ns.Collection))
        containers = [self.graph_to_dict(g, sbj, self.properties['CollectionObject']) for sbj in subjects]
        for c in containers:
            c['capabilities'] = CollectionCapabilities(**c['capabilities'])
            c['properties'] = CollectionProperties(**c['properties'])
        return [CollectionObject(**c) for c in containers]

    '''
        Convert a collection object into a set of triples,
        using Base64 encoding for URL conformant IDs and
        #capabilities and #properties fragments
    '''
    def collection_to_graph(self,c_obj):
        node = self.marmotta.ldp(encoder.encode(c_obj.id))
        g = Graph(identifier=node)
        g.add((node,RDF.type, self.ns.Collection))
        self.dict_to_graph(c_obj.dict(), subject=node, map=self.inverted_properties['CollectionObject'], g=g)
        return g

    def graph_to_member(self,g):
        subjects = [s for s in g.subjects(RDF.type, self.ns.Member)]
        for sbj in subjects:
            g.remove((sbj,RDF.type,self.ns.Member))
        members = [self.graph_to_dict(g, sbj, self.properties['MemberItem']) for sbj in subjects]
        for m in members:
            if m.get('mappings') is not None:
                # todo: probably allows for false positives
                m['mappings'] = CollectionItemMappingMetadata(**m['mappings'])
        return [MemberItem(**m) for m in members]

    def member_to_graph(self, c_id, m_obj):
        m_dict = m_obj.dict()
        node = self.marmotta.ldp(encoder.encode(c_id)+"/member/"+encoder.encode(m_obj.id))
        g = Graph(identifier=node)
        g.add((node, RDF.type, self.ns.Member))
        self.dict_to_graph(m_dict, subject=node, map=self.inverted_properties['MemberItem'], g=g)
        return g

    def graph_to_service(self, g):
        subjects = [s for s in g.subjects(RDF.type, self.ns.Service)]
        for sbj in subjects:
            g.remove((sbj,RDF.type,self.ns.Service))
        services = [sbj for sbj in subjects]
        if len(services) is 1:
            service = services.pop()
            return Service(**self.graph_to_dict(g, service, self.properties['ServiceFeatures']))
        else:
            raise KeyError

    def service_to_graph(self,s_obj):
        node = self.marmotta.ldp("service")
        g = Graph(identifier=node)
        g.add((node, RDF.type, self.ns.Service))
        self.dict_to_graph(s_obj.dict(), subject=node, map=self.inverted_properties['ServiceFeatures'], g=g)
        return g