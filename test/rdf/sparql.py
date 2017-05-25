from unittest import TestCase
from rdflib import Variable
from rdflib.plugins.sparql.results.jsonresults import JSONResult

from src.utils.rdf.sparql import SPARQLTools
from test.mock import RandomGenerator


class SPARQLTest(TestCase):

    def setUp(self):
        self.mock = RandomGenerator()
        self.sparql = SPARQLTools()

    def test_ldp_result_to_dataset(self):
        result = self.mock.collection_result()
        b = result.bindings
        ds = self.sparql.result_to_dataset(result)
        g = Variable('g')
        s = Variable('s')
        p = Variable('p')
        o = Variable('o')
        self.assertEqual(len(b), len(ds))
        for d in result.bindings:
            self.assertIn((d[s], d[p], d[o], d[g]), ds)

# todo: create result / dataset mocks
