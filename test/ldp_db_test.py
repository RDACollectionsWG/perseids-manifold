from rdflib import Dataset
from rdflib.plugins.sparql.results.jsonresults import JSONResult
from src.data.ldp_db import LDPDataBase
from src.utils.queries import reset_marmotta
from src.utils.url_encoder import encoder
from unittest import TestCase, main
from flask import json
from random import randint
from run import app
from .mock import RandomGenerator
import os, requests


class DbTests(TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n// Test LDP DB ------------------")

    def setUp(self):
        self.server = os.environ.get('COLLECTIONS_API_TEST_DB')
        if not self.server:
            raise EnvironmentError
        self.db = LDPDataBase(self.server)
        requests.post(self.db.marmotta.sparql.update, data=reset_marmotta)
        self.mock = RandomGenerator()

    #def test_ldp_b64encode(self):
     #   self.assertEqual(self.db.b64encode(self.server),"aHR0cDovL2xvY2FsaG9zdDozMjc2OC9tYXJtb3R0YQ==")

    def tearDown(self):
        requests.post(self.db.marmotta.sparql.update, data=reset_marmotta)

    #def test_ldp_b64decode(self):
    #    self.assertEqual(self.db.b64decode("aHR0cDovL2xvY2FsaG9zdDozMjc2OC9tYXJtb3R0YQ=="),self.server)

    #def test_ldp_b64_roundtrip(self):
    #    self.assertEqual(self.db.b64decode(self.db.b64encode(self.server)),self.server)

    #def test_ldp_graph_to_dict(self):
    #    self.db.graph_to_dict(graph, node, propertiesMap)

    #def test_ldp_dict_to_graph(self):
    #    assert False
    #    self.db.dict_to_graph()

    #def test_ldp_collection_to_graph(self):
    #    assert False
    #    self.db.collection_to_graph()

    #def test_ldp_graph_to_collection(self):
    #    assert False
    #    self.db.graph_to_collection()

    #def test_ldp_member_to_graph(self):
    #    assert False
    #    self.db.member_to_graph()

    #def test_ldp_graph_to_member(self):
    #    assert False
    #    self.db.graph_to_member()

    #def test_ldp_service_to_graph(self):
    #    assert False
    #    self.db.service_to_graph()

    #def test_ldp_graph_to_service(self):
    #    assert False
    #    self.db.graph_to_service()

    #def test_ldp_result_to_dataset(self):
    #    assert False
    #    self.db.result_to_dataset()

    #def test_ldp_add_contains(self):
    #    assert False
    #    self.db.ldp_add_contains()

    def test_ldp_create_collection(self):
        with app.app_context():
            c_obj = self.mock.collection()
            id = self.db.marmotta.ldp(encoder.encode(c_obj.id))
            self.db.set_collection(c_obj)
            response = requests.post(self.db.marmotta.sparql.select,data=self.db.sparql.collections.select(id),headers={"Accept":"application/sparql-results+json"})
            #print(response.json())
            r_obj = self.db.RDA.graph_to_collection(self.db.sparql.result_to_dataset(JSONResult(response.json())).graph(id)).pop()
            self.assertDictEqual(c_obj.dict(), r_obj.dict())

    def test_ldp_access_created_collection(self):
         with app.app_context():
             # todo: post collection to sparql, retrieve via LDP and compare
             c_obj = self.mock.collection()
             self.db.set_collection(c_obj)
             r_obj = self.db.get_collection(c_obj.id).pop()
             self.assertDictEqual(c_obj.dict(), r_obj.dict())

    def test_ldp_access_multiple_collections(self):
         with app.app_context():
             # todo: post collections to sparql, retrieve via LDP and compare
             c_objs = [self.mock.collection() for _ in range(randint(2, 5))]
             for c in c_objs:
                 self.db.set_collection(c)
             self.assertSetEqual(set([json.dumps(c) for c in c_objs]), set([json.dumps(c) for c in self.db.get_collection()]))

    def test_ldp_access_with_ldp(self):
        with app.app_context():
            # todo: post collection to sparql, retrieve via LDP and compare
            c_obj = self.mock.collection()
            self.db.set_collection(c_obj)
            g = Dataset().parse(self.db.marmotta.ldp(encoder.encode(c_obj.id)), format="n3")
            r_obj = self.db.RDA.graph_to_collection(g).pop()
            self.assertDictEqual(c_obj.dict(), r_obj.dict())

    def test_ldp_delete_created_collection(self):
         with app.app_context():
             c_obj = self.mock.collection()
             self.db.set_collection(c_obj)
             self.db.del_collection(c_obj.id)
             with self.assertRaises(KeyError) as context:
                self.db.get_collection(c_obj.id)

    def test_ldp_overwrite_collection(self):
         with app.app_context():
             c_obj = self.mock.collection()
             d_obj = self.mock.collection()
             d_obj.id = c_obj.id
             d_obj.capabilities.isOrdered = not c_obj.capabilities.isOrdered
             self.db.set_collection(c_obj)
             self.assertNotEqual(self.db.get_collection(c_obj.id).pop().capabilities.isOrdered, d_obj.capabilities.isOrdered)
             self.db.upd_collection(d_obj)
             self.assertEqual(self.db.get_collection(c_obj.id).pop().capabilities.isOrdered, d_obj.capabilities.isOrdered)

    def test_db_create_member(self):
         with app.app_context():
             c_obj = self.mock.collection()
             m_obj = self.mock.member()
             id = self.db.marmotta.ldp(encoder.encode(c_obj.id)+"/member/"+encoder.encode(m_obj.id))
             self.db.set_collection(c_obj)
             self.db.set_member(c_obj.id, m_obj)
             response = requests.post(self.db.marmotta.sparql.select,data=self.db.sparql.members.select(id),headers={"Accept":"application/sparql-results+json"})
             r_obj = self.db.RDA.graph_to_member(self.db.sparql.result_to_dataset(JSONResult(response.json())).graph(id)).pop()
             self.assertDictEqual(m_obj.dict(),r_obj.dict())

    def test_db_access_created_member(self):
         with app.app_context():
             c_obj = self.mock.collection()
             m_obj = self.mock.member()
             self.db.set_collection(c_obj)
             self.db.set_member(c_obj.id, m_obj)
             self.assertEqual(json.dumps(m_obj), json.dumps(self.db.get_member(c_obj.id, m_obj.id).pop()))

    def test_db_access_multiple_members(self):
         with app.app_context():
             c_obj = self.mock.collection()
             self.db.set_collection(c_obj)
             m_objs = [self.mock.member() for _ in range(randint(2, 5))]
             for m_obj in m_objs:
                 self.db.set_member(c_obj.id, m_obj)
             self.assertSetEqual(set([json.dumps(m) for m in m_objs]), set([json.dumps(m) for m in self.db.get_member(c_obj.id)]))

    def test_db_delete_created_member(self):
         with app.app_context():
             c_obj = self.mock.collection()
             m_obj = self.mock.member()
             self.db.set_collection(c_obj)
             self.db.set_member(c_obj.id, m_obj)
             self.assertTrue(len(self.db.get_member(c_obj.id, m_obj.id)) == 1)
             self.db.del_member(c_obj.id, m_obj.id)
             with self.assertRaises(KeyError) as context:
                 self.db.get_member(c_obj.id, m_obj.id)

    def test_db_overwrite_member(self):
         with app.app_context():
             c_obj = self.mock.collection()
             m_obj = self.mock.member()
             n_obj = self.mock.member()
             n_obj.id = m_obj.id
             n_obj.location = m_obj.location+"x"
             self.db.set_collection(c_obj)
             self.db.set_member(c_obj.id, m_obj)
             self.db.upd_member(c_obj.id, n_obj)
             self.assertEqual(self.db.get_member(c_obj.id, m_obj.id)[0].location, n_obj.location)

    def test_db_create_service(self):
         with app.app_context():
             s_obj = self.mock.service()
             self.db.set_service(s_obj)
             self.assertDictEqual(self.db.get_service().dict(),s_obj.dict())

    # def test_db_access_created_service(self):
    #     with app.app_context():
    #         s_obj = self.mock.service()
    #         self.db.set_service(s_obj)
    #         t_obj = self.db.get_service()
    #         self.assertEqual(json.dumps(s_obj), json.dumps(t_obj))
    #
    # def test_db_overwrite_service(self):
    #     with app.app_context():
    #         s_obj = self.mock.service()
    #         t_obj = self.mock.service()
    #         t_obj.providesCollectionPids = not s_obj.providesCollectionPids
    #         self.db.set_service(s_obj)
    #         self.db.set_service(t_obj)
    #         self.assertNotEqual(json.dumps(s_obj), json.dumps(self.db.get_service()))

if __name__ == '__main__':
    main()