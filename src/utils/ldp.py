from rdflib import Namespace, Graph, Literal
from rdflib.namespace import RDF, DCTERMS
from datetime import datetime

class LDPModelExtension:
    
    def __init__(self):
        self.ns = Namespace("http://www.w3.org/ns/ldp#")
    
    def add_contains(self, container, member, basic=True):
        g = Graph(identifier=self.ns)
        g.add((container, self.ns.contains, member))
        g.add((member, RDF.type, self.ns.RDFSource))
        g.add((member, RDF.type, self.ns.Resource))
        g.add((member, DCTERMS.created, Literal(datetime.utcnow())))
        g.add((member, DCTERMS.modified, Literal(datetime.utcnow())))
        if basic:
            g.add((member, RDF.type, self.ns.BasicContainer))
            g.add((member, RDF.type, self.ns.Container))
            g.add((member, self.ns.interactionModel, self.ns.BasicContainer))
        return g

LDP = LDPModelExtension()