from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, OWL
from src.utils.data.db import DBMeta
from src.utils.base.models import Model
import abc

class MappingTool:

    def __init__(self, ns, dictionary):
        self.ns = ns
        self.dictionary = dictionary

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
            elif prd == RDF.type and obj == OWL.Nothing:
                dct.update({})
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
            items = [(k,v) for k,v in val.items() if not k.startswith("__")]
            if len(items) is 0:
                g.add((subject,URIRef(map.get(key, {'label': RDF.type})['label']), OWL.Nothing))
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

    def object_to_graph(self, node, obj):
        assert isinstance(node,URIRef)
        assert isinstance(obj, Model)
        g = Graph(identifier=node)
        g.add((node, RDF.type, self.dictionary.get(type(obj)).uri))
        return self.dict_to_graph(obj.dict(), subject=node, map=self.dictionary.get(type(obj)).inverted, g=g)

    def graph_to_object(self, g):
        subjects = [(s,o) for s,o in g.subject_objects(RDF.type) if o in set(v.uri for v in self.dictionary.values())]
        for sbj,obj in subjects:
            g.remove((sbj, RDF.type, obj))
        objects = [(self.graph_to_dict(g, s, self.dictionary.get(o).map), o) for s,o in subjects]
        return [self.dictionary.get(o).type(**d) for d,o in objects]
