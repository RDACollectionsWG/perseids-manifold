import unittest
from rdflib.namespace import RDF
from src.utils.rda import RDATools
from src.utils.marmotta import Marmotta
from test.mock import RandomGenerator


class RDATestCase(unittest.TestCase):

    def setUp(self):
        self.mock = RandomGenerator()
        self.rda = RDATools(Marmotta("http://localhost:8080/marmotta/"))

    def test_rda_graph_to_dict(self):
        obj = self.mock.collection()
        g = self.mock.graph_collection(self.rda.marmotta.ldp(""), obj)
        g.remove((None, RDF.type, self.rda.ns.Collection))
        dct = self.rda.graph_to_dict(g,g.identifier,self.rda.properties['CollectionObject'])
        self.assertDictEqual(obj.dict(), dct)

    def test_rda_dict_to_graph(self):
        obj = self.mock.collection()
        dct = obj.dict()
        g1 = self.mock.graph_collection(self.rda.marmotta.ldp(""), obj)
        g1.remove((None, RDF.type, self.rda.ns.Collection))
        g2 = self.rda.dict_to_graph(dct,subject=g1.identifier,map=self.rda.inverted_properties['CollectionObject'])
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_collection_to_graph(self):
        obj = self.mock.collection()
        g1 = self.mock.graph_collection(self.rda.marmotta.ldp(""), obj)
        g2 = self.rda.collection_to_graph(obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_collection(self):
        obj1 = self.mock.collection()
        g = self.mock.graph_collection(self.rda.marmotta.ldp(""), obj1)
        obj2 = self.rda.graph_to_collection(g).pop()
        self.assertDictEqual(obj1.dict(),obj2.dict())

    def test_rda_member_to_graph(self):
        cid = self.mock.collection().id
        obj = self.mock.member()
        g1 = self.mock.graph_member(self.rda.marmotta.ldp(""), cid, obj)
        g2 = self.rda.member_to_graph(cid, obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_member(self):
        cid = self.mock.collection().id
        obj1 = self.mock.member()
        g = self.mock.graph_member(self.rda.marmotta.ldp(""), cid, obj1)
        obj2 = self.rda.graph_to_member(g).pop()
        self.assertDictEqual(obj1.dict(),obj2.dict())

    def test_rda_service_to_graph(self):
        obj = self.mock.service()
        g1 = self.mock.graph_service(self.rda.marmotta.ldp(""), obj)
        g2 = self.rda.service_to_graph(obj)
        self.assertEqual(len(g1), len(g2))
        self.assertEqual(len(g1-g2), 0)
        self.assertEqual(len(g2-g1), 0)

    def test_rda_graph_to_service(self):
        obj1 = self.mock.service()
        g = self.mock.graph_service(self.rda.marmotta.ldp(""), obj1)
        obj2 = self.rda.graph_to_service(g)
        self.assertDictEqual(obj1.dict(),obj2.dict())

    #def test_ldp_add_contains(self):
    #    assert False
    #    self.db.ldp_add_contains()


if __name__ == '__main__':
    unittest.main()
