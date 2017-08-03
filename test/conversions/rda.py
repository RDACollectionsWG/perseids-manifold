import unittest

from rdflib.namespace import RDF

from src.utils.conversions.rda import RDATools, RDA
from src.utils.ids.marmotta import Marmotta
from src.utils.conversions.rdf import MappingTool
from test.mock import RandomGenerator


class RDATestCase(unittest.TestCase):

    def setUp(self):
        #self.maxDiff = None
        self.mock = RandomGenerator()
        self.marmotta = Marmotta("http://localhost:8080/marmotta")
        self.rda = MappingTool(RDA, RDATools)
        self.maxDiff = None

    def test_rda_graph_to_dict(self):
        obj = self.mock.collection()
        g = self.mock.graph_collection(self.marmotta.ldp(""), obj)
        g.remove((None, RDF.type, self.rda.ns.Collection))
        dct = self.rda.graph_to_dict(g,g.identifier,self.rda.dictionary.get(type(obj)).map)
        self.assertDictEqual(obj.dict(), dct)

    def test_rda_dict_to_graph(self):
        obj = self.mock.collection()
        dct = obj.dict()
        g1 = self.mock.graph_collection(self.marmotta.ldp(""), obj)
        g1.remove((None, RDF.type, self.rda.ns.Collection))
        g2 = self.rda.dict_to_graph(dct,subject=g1.identifier,map=self.rda.dictionary.get(type(obj)).inverted)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_collection_to_graph(self):
        obj = self.mock.collection()
        g1 = self.mock.graph_collection(self.marmotta.ldp(""), obj)
        g2 = self.rda.object_to_graph(g1.identifier, obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_collection(self):
        obj1 = self.mock.collection()
        g = self.mock.graph_collection(self.marmotta.ldp(""), obj1)
        obj2 = self.rda.graph_to_object(g).pop()
        self.assertDictEqual(obj1.dict(),obj2.dict())

    def test_rda_member_to_graph(self):
        cid = self.mock.collection().id
        obj = self.mock.member()
        g1 = self.mock.graph_member(self.marmotta.ldp(""), cid, obj)
        g2 = self.rda.object_to_graph(g1.identifier, obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_member(self):
        cid = self.mock.collection().id
        obj1 = self.mock.member()
        g = self.mock.graph_member(self.marmotta.ldp(""), cid, obj1)
        obj2 = self.rda.graph_to_object(g).pop()
        self.assertDictEqual(obj1.dict(),obj2.dict())

    def test_rda_service_to_graph(self):
        obj = self.mock.service()
        g1 = self.mock.graph_service(self.marmotta.ldp(""), obj)
        g2 = self.rda.object_to_graph(g1.identifier, obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_service(self):
        obj1 = self.mock.service()
        g = self.mock.graph_service(self.marmotta.ldp(""), obj1)
        obj2 = self.rda.graph_to_object(g).pop()
        self.assertDictEqual(obj1.dict(),obj2.dict())

        #def test_ldp_add_contains(self):
        #    assert False
        #    self.db.ldp_add_contains()


if __name__ == '__main__':
    unittest.main()