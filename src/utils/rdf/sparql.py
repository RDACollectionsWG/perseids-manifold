from requests import post
from rdflib import URIRef, Dataset, Variable
from rdflib.plugins.sparql.results.jsonresults import JSONResult
from src.utils.base.struct import Struct
from src.utils.base.errors import DBError


# todo: the queries could be consolidated into a single set with a few more parameters
# todo: it's cleaner architecture but more complex interface - do it anyways?

def result_to_dataset(result):
    ds = Dataset()
    for q in result.bindings:
        ds.add((q[Variable('s')],q[Variable('p')],q[Variable('o')],q[Variable('g')]))
    return ds

class SPARQLSet(JSONResult):

    def __init__(self, json, status_code):
        super().__init__(json)
        self.status_code = status_code

    def toDataset(self):
        return result_to_dataset(self)

class SPARQLTools:

    def __init__(self, server):
        self.server = server
        self.queries=Struct(
            # todo: same
            list=lambda g=None, s=None, p=None, o=None: '''
                SELECT ?g ?s ?p ?o WHERE {{
                {}
                GRAPH ?g {{ ?s ?p ?o }}
                }}
            '''.format('\n'.join(['BIND ({} as ?{})'.format(v.n3(),k) for k,v in {'g':g, 's':s, 'p':p, 'o':o}.items() if v is not None])).encode(),
            # todo: pattern same
            delete=lambda id: '''
                DELETE {{GRAPH ?grph {{?sub ?pred ?obj}} }} WHERE {{
                BIND("^{}(/member|$).*" AS ?pattern)
                GRAPH ?grph {{ ?sub ?pred ?obj }}
                FILTER(REGEX(STR(?grph), ?pattern) || REGEX(STR(?sub), ?pattern) || REGEX(STR(?obj), ?pattern))
                }}
            '''.format(id).encode(),
            # todo: same
            select=lambda ids: '''
                SELECT ?g ?s ?p ?o WHERE {{
                values ?g {{ {} }}
                GRAPH ?g {{ ?s ?p ?o }}
                }}
            '''.format(' '.join([i.n3() for i in ids])).encode(),
            # todo: remove?
            selectddd=lambda id: '''SELECT ?g ?s ?p ?o WHERE {{
                BIND("^{}($|/member.*)" AS ?pattern)
                GRAPH ?g {{ ?s ?p ?o }}
                FILTER(REGEX(STR(?g), ?pattern) || REGEX(STR(?s), ?pattern) || REGEX(STR(?o), ?pattern))
                }}
            '''.format(id).encode(),
            # todo: same
            insert=lambda dataset: '''
                INSERT DATA {{ {} }}
            '''.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode(),
            # todo: different classes
            ask=lambda id, type: '''
                ASK WHERE {{
                {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> {}
                }}
            '''.format(id.n3(), type.n3()).encode(),
            # todo: specific to collections
            size=lambda id: '''
                SELECT (COUNT(?x) AS ?size) WHERE {{
                <{}/member> <http://www.w3.org/ns/ldp#contains> ?x
                }}
            '''.format(str(id)).encode(),
            # todo: class should be either Member or Collection
            find=lambda ids, type=URIRef("http://www.w3.org/ns/ldp#Container"): '''
                SELECT (COUNT(?x) AS ?size) WHERE {{
                values ?x {{ {} }}
                ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> {} .
                }}
            '''.format(' '.join([id.n3() for id in ids]), type.n3()).encode(),
            asky=lambda id: 'ASK WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rd-alliance.org/ns/collections#Member> }}'.format(id.n3()).encode()
        )
        self.service=Struct(
            select=lambda id: 'SELECT ?g ?s ?p ?o WHERE {{ BIND( {} AS ?s ) GRAPH ?g {{ ?s ?p ?o }} }}'.format(id.n3()).encode(),
            insert=lambda dataset: 'INSERT DATA {{ {} }}'.format('\n'.join(['GRAPH {} {{ {} }}'.format(g.identifier.n3(), '\n'.join(['{} {} {} .'.format(t[0].n3(),t[1].n3(),t[2].n3()) for t in g.triples((None,None,None))])) for g in dataset.graphs() if not g.identifier==URIRef('urn:x-rdflib:default')])).encode(),
            ask=lambda id: 'ASK WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rd-alliance.org/ns/collections#Service> }}'.format(id.n3()).encode()
        )

    def request(self, query, server):
        if server is self.server.select:
            response = post(server, data=query, headers={"Accept":"application/sparql-results+json", "Content-Type":"application/sparql-select"})
            # print("SPARQL ERROR CODE: ", response.status_code)
        else:
            response = post(server, data=query, headers={"Content-Type":"application/sparql-update; charset=utf-8"})
        if response.status_code is not 200:
            raise DBError()
        else:
            json = {'head':{'vars':[]},'results':{'bindings':[]}}
            try:
                json = response.json()
            finally:
                return SPARQLSet(json, response.status_code)

    def list(self, g=None, s=None, p=None, o=None):
        if not (g or s or p or o):
            raise DBError()
        query=self.queries.list(g,s,p,o)
        return self.request(query, self.server.select)

    def select(self, ids):
        if not isinstance(ids, list):
            ids = [ids]
        for id in ids:
            if not isinstance(id, URIRef):
                raise DBError()
        query = self.queries.select(ids)
        return self.request(query, self.server.select)

    def insert(self, dataset):
        if not isinstance(dataset, Dataset):
            raise DBError()
        query = self.queries.insert(dataset)
        return self.request(query, self.server.update)

    def delete(self, id):
        if not isinstance(id, URIRef):
            raise DBError()
        query = self.queries.delete(id)
        return self.request(query, self.server.update)

    def ask(self, id, type):
        if not isinstance(id, URIRef):
            raise DBError()
        query = self.queries.ask(id, type)
        return self.request(query, self.server.select)

    def size(self, id):
        if not isinstance(id, URIRef):
            raise DBError()
        query = self.queries.size(id)
        return self.request(query, self.server.select)

    def find(self, ids, type):
        if not isinstance(ids, list):
            ids = [ids]
        for id in ids:
            if not isinstance(id, URIRef):
                raise DBError()
        if not isinstance(type, URIRef):
            raise DBError()
        query = self.queries.find(ids, type)
        return self.request(query, self.server.select)

    def result_to_dataset(self, result):
        return result_to_dataset(result)
