import random
import string
from unittest import TestCase
from rdflib import Namespace, URIRef
from src.utils.ids.marmotta import Marmotta

class MarmottaTest(TestCase):

    def setUp(self):
        self.host = 'http://'+''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))+'.org'
        self.marmotta = Marmotta(self.host)

    def test_marmotta_server(self):
        slug = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))
        self.assertIsInstance(self.marmotta.server, Namespace)
        self.assertIsInstance(self.marmotta.server[slug], URIRef)
        self.assertEqual(str(self.marmotta.server[slug]), self.host+"/"+slug)

    def test_marmotta_ldp(self):
        slug = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))
        #self.assertIsInstance(self.marmotta.ldp, classmethod) todo: check for method type
        self.assertIsInstance(self.marmotta.ldp(slug), URIRef)
        self.assertEqual(str(self.marmotta.ldp(slug)), self.host+"/ldp/"+slug)

    def test_marmotta_sparql(self):
        self.assertTrue(self.marmotta.sparql.select == URIRef(self.host+"/sparql/select"))
        self.assertTrue(self.marmotta.sparql.update == URIRef(self.host+"/sparql/update"))
