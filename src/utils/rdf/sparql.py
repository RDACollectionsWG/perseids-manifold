from rdflib import URIRef, Dataset, Variable

from src.utils.base.struct import Struct


# todo: the queries could be consolidated into a single set with a few more parameters
# todo: it's cleaner architecture but more complex interface - do it anyways?

class SPARQLSet:

    def __init__(self, list=None, select=None, delete=None, insert=None, update=None, ask=None):
        self.list = list
        self.select = select
        self.delete = delete
        self.insert = insert
        self.update = update
        self.ask = ask

class SPARQLTools:

    def __init__(self):
        self.collections=Struct(
            list=lambda g=None, s=None, p=None, o=None: "SELECT ?g ?s ?p ?o WHERE {{ {} GRAPH ?g {{ ?s ?p ?o }} }}".format(" ".join(["BIND ({} as ?{})".format(v.n3(),k) for k,v in {"g":g, "s":s, "p":p, "o":o}.items() if v is not None])).encode(),
            delete=lambda id: 'DELETE {{GRAPH ?grph {{?sub ?pred ?obj}} }} WHERE {{ BIND("^{}(/member|$).*" AS ?pattern) GRAPH ?grph {{ ?sub ?pred ?obj }} FILTER(REGEX(STR(?grph), ?pattern) || REGEX(STR(?sub), ?pattern) || REGEX(STR(?obj), ?pattern)) }}'.format(id).encode(),
            selects=lambda ids: '''SELECT ?g ?s ?p ?o WHERE {{
                values ?g {{ {} }}
                GRAPH ?g {{ ?s ?p ?o }} }}
            '''.format(' '.join([i.n3() for i in ids])).encode(),
            select=lambda id: 'SELECT ?g ?s ?p ?o WHERE {{ BIND("^{}($|/member.*)" AS ?pattern) GRAPH ?g {{ ?s ?p ?o }} FILTER(REGEX(STR(?g), ?pattern) || REGEX(STR(?s), ?pattern) || REGEX(STR(?o), ?pattern)) }}'.format(id).encode(),
            insert=lambda dataset: 'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode(),
            update=lambda dataset: [
                'DELETE {{GRAPH ?grph {{?sub ?pred ?obj}} }} WHERE {{ BIND("^{}$" AS ?pattern) GRAPH ?grph {{ ?sub ?pred ?obj }} FILTER(REGEX(STR(?grph), ?pattern) || REGEX(STR(?sub), ?pattern) || REGEX(STR(?obj), ?pattern)) }}'.format(id).encode(),
                'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode()
            ],
            ask=lambda id: 'ASK WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rd-alliance.org/ns/collections#Collection> }}'.format(id.n3()).encode(),
            size=lambda id: 'SELECT (COUNT(?x) AS ?size) WHERE {{ <{}/member> <http://www.w3.org/ns/ldp#contains> ?x }}'.format(str(id)).encode()
        )
        self.members=Struct(
            list=lambda g=None, s=None, p=None, o=None: "SELECT ?g ?s ?p ?o WHERE {{ {} GRAPH ?g {{ ?s ?p ?o }} }}".format(" ".join(["BIND ({} as ?{})".format(v.n3(),k) for k,v in {"g":g, "s":s, "p":p, "o":o}.items() if v is not None])).encode(),
            delete=lambda id: 'DELETE {{GRAPH ?grph {{?sub ?pred ?obj}} }} WHERE {{ BIND("^{}$" AS ?pattern) GRAPH ?grph {{ ?sub ?pred ?obj }} FILTER(REGEX(STR(?grph), ?pattern) || REGEX(STR(?sub), ?pattern) || REGEX(STR(?obj), ?pattern)) }}'.format(id).encode(),
            selects=lambda ids: '''SELECT ?g ?s ?p ?o WHERE {{
                values ?g {{ {} }}
                GRAPH ?g {{ ?s ?p ?o }} }}
            '''.format(' '.join([i.n3() for i in ids])).encode(),
            select=lambda id: 'SELECT ?g ?s ?p ?o WHERE {{ BIND("^{}$" AS ?pattern) GRAPH ?g {{ ?s ?p ?o }} FILTER(REGEX(STR(?g), ?pattern) || REGEX(STR(?s), ?pattern) || REGEX(STR(?o), ?pattern)) }}'.format(id).encode(),
            insert=lambda dataset: 'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode(),
            update=lambda dataset: [
                'DELETE {{GRAPH ?grph {{?sub ?pred ?obj}} }} WHERE {{ BIND("^{}$" AS ?pattern) GRAPH ?grph {{ ?sub ?pred ?obj }} FILTER(REGEX(STR(?grph), ?pattern) || REGEX(STR(?sub), ?pattern) || REGEX(STR(?obj), ?pattern)) }}'.format(id).encode(),
                'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode()
            ],
            ask=lambda id: 'ASK WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rd-alliance.org/ns/collections#Member> }}'.format(id.n3()).encode()
        )
        self.service=Struct(
            select=lambda id: 'SELECT ?g ?s ?p ?o WHERE {{ BIND( {} AS ?s ) GRAPH ?g {{ ?s ?p ?o }} }}'.format(id.n3()).encode(),
            insert=lambda dataset: 'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode(),
            ask=lambda id: 'ASK WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rd-alliance.org/ns/collections#Service> }}'.format(id.n3()).encode()
        )

    def result_to_dataset(self, result):
        ds = Dataset()
        for q in result.bindings:
            ds.add((q[Variable('s')],q[Variable('p')],q[Variable('o')],q[Variable('g')]))
        return ds
