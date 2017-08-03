from rdflib import Literal, URIRef, Namespace
from rdflib.namespace import DCTERMS

from src.collections.models import *
from src.members.models import MemberItem
from src.service.models import Service

boolean = lambda x: True if str(x)=='true' else False

RDA = Namespace("http://rd-alliance.org/ns/collections#")

class dictionary:

    def __init__(self):
        self.dct = {}

    def get(self, key):
        return self.dct.get(key)

    def add(self, dct):
        assert isinstance(dct, entry)
        self.dct.update({dct.uri:dct, dct.type: dct})

    def values(self):
        return self.dct.values()

class entry:

    def __init__(self, cls, uri, map):
        assert isinstance(cls, type)
        assert isinstance(uri, URIRef)
        assert isinstance(map, dict)
        self.type = cls
        self.uri = uri
        self.map = map
        self.inverted = self.invert(self.map)

    def invert(self, dct):
        return {v['label']: {'label':k, 'type':v['type'], 'rdf': v['rdf'], 'map':self.invert(v['map'])} for k,v in dct.items() if not k.startswith("__")}

RDATools = dictionary()
RDATools.add(entry(CollectionObject, RDA.Collection, {
    str(DCTERMS.identifier): {'label': 'id', 'type': str, 'rdf': Literal, 'map': {}},
    str(DCTERMS.description): {'label': 'description', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#description"), 'map': {}},
    str(RDA.hasCapabilities): {'label': 'capabilities', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#capabilities"), 'map': {
        str(RDA.isOrdered): {'label': 'isOrdered', 'type': boolean, 'rdf': Literal, 'map': {}},
        str(RDA.appendsToEnd): {'label': 'appendsToEnd', 'type': boolean, 'rdf': Literal, 'map': {}},
        str(RDA.maxLength): {'label': 'maxLength', 'type': int, 'rdf': Literal, 'map': {}},
        str(RDA.membershipIsMutable): {'label': 'membershipIsMutable', 'type': boolean, 'rdf': Literal, 'map': {}},
        str(RDA.metadataIsMutable): {'label': 'metadataIsMutable', 'type': boolean, 'rdf': Literal, 'map': {}},
        str(RDA.restrictedToType): {'label': 'restrictedToType', 'type': str, 'rdf': Literal, 'map': {}},
        str(RDA.supportsRoles): {'label': 'supportsRoles', 'type': boolean, 'rdf': Literal, 'map': {}},
    }},  # todo: fix URIs
    str(RDA.hasProperties): {'label': 'properties', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+"#properties"), 'map': {
        str(RDA.modelType): {'label': 'modelType', 'type': str, 'rdf': URIRef, 'map': {}},
        str(RDA.descriptionOntology): {'label': 'descriptionOntology', 'type': str, 'rdf': URIRef, 'map': {}},
        str(RDA.memberOf): {'label': 'memberOf', 'type': str, 'rdf': URIRef, 'map': {}},
        str(DCTERMS.license): {'label': 'license', 'type': str, 'rdf': Literal, 'map': {}},
        str(DCTERMS.rightsHolder): {'label': 'ownership', 'type': str, 'rdf': Literal, 'map': {}},
        str(RDA.hasAccessRestrictions): {'label': 'hasAccessRestrictions', 'type': boolean, 'rdf': Literal, 'map': {}}
    }}
}))
RDATools.add(entry(MemberItem, RDA.Member, {
    str(DCTERMS.identifier): {'label': 'id', 'type': str, 'rdf': Literal, 'map': {}},
    str(RDA.location): {'label': 'location', 'type': str, 'rdf': Literal, 'map': {}},
    str(RDA.datatype): {'label': 'datatype', 'type': str, 'rdf': Literal, 'map': {}},
    str(RDA.ontology): {'label': 'ontology', 'type': str, 'rdf': Literal, 'map': {}},
    str(RDA.mappings): {'label': 'mappings', 'type': lambda x: x, 'rdf': lambda x: URIRef(x+'#mappings'), 'map': {
        str(RDA.role): {'label': 'role', 'type': str, 'rdf': Literal, 'map': {}},
        str(RDA.itemIndex): {'label': 'index', 'type': int, 'rdf': Literal, 'map': {}},
        str(RDA.dateAdded): {'label': 'dateAdded', 'type': str, 'rdf': Literal, 'map': {}}
    }}
}))
RDATools.add(entry(Service, RDA.Service, {
    str(RDA.providesCollectionPids): {'label': 'providesCollectionPids', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.collectionPidProviderType): {'label': 'collectionPidProviderType', 'type': str, 'rdf': Literal, 'map': {}}, # todo: URIRef?
    str(RDA.enforcesAccess): {'label': 'enforcesAccess', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.supportsPagination): {'label': 'supportsPagination', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.asynchronousActions): {'label': 'asynchronousActions', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.ruleBasedGeneration): {'label': 'ruleBasedGeneration', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.maxExpansionDepth): {'label': 'maxExpansionDepth', 'type': int, 'rdf': Literal, 'map': {}},
    str(RDA.providesVersioning): {'label': 'providesVersioning', 'type': boolean, 'rdf': Literal, 'map': {}},
    str(RDA.supportedCollectionOperations): {'label': 'supportedCollectionOperations', 'type': str, 'rdf': Literal, 'map': {}},
    str(RDA.supportedModelTypes): {'label': 'supportedModelTypes', 'type': str, 'rdf': URIRef, 'map': {}}
}))