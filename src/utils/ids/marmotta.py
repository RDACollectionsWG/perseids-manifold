from rdflib import Namespace

from src.utils.base.struct import Struct


class Marmotta:

    def __init__(self, srv):
        self.server = Namespace(srv) if srv.endswith("/") else Namespace(srv+"/")
        self.ldp = lambda slug=None: self.server.ldp if slug is None else self.server["ldp"+slug[:-1]] if slug.startswith("/") and slug.endswith("/") else self.server["ldp"+slug] if slug.startswith("/") else self.server["ldp/"+slug[:-1]] if slug.endswith("/") else self.server["ldp/"+slug]
        self.sparql = Struct(select=self.server["sparql/select"], update=self.server["sparql/update"])
