import base64
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, DCTERMS
from src.data.ldp_db import *
from src.collections.models import *
from src.members.models import *
from test.mock import RandomGenerator

mocks = RandomGenerator()
c_obj = mocks.collection()
ldp = LDPDataBase("http://localhost:32768/marmotta")
