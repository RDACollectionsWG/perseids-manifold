from src.data.db import DataBase
from unittest import TestCase, main
from flask import json
from tempfile import TemporaryDirectory, mkdtemp
from random import randint
from run import app
from .mock import RandomGenerator
import os


class DbTests(TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n// Test Filesystem DB ------------------")

    def setUp(self):
        self.dir = TemporaryDirectory(dir='test/data')
        #self.dir = mkdtemp(dir='./test/data')
        self.db = DataBase(self.dir.name)
        self.mock = RandomGenerator()

    def tearDown(self):
        # a = 'b'
        self.dir.cleanup()

    def test_db_create_collection_on_filesystem(self):
        with app.app_context():
            c_obj = self.mock.collection()
            self.db.setCollection(c_obj)
            self.assertTrue(os.path.isfile(os.path.join(self.db.d_data, c_obj.id.replace('/', '∕'), self.db.d_collection)))

    def test_db_access_created_collection(self):
        with app.app_context():
            c_obj = self.mock.collection()
            self.db.setCollection(c_obj)
            self.assertEqual(json.dumps(c_obj), json.dumps(self.db.getCollections(c_obj.id).pop()))

    def test_db_access_multiple_collections(self):
        with app.app_context():
            c_objs = [self.mock.collection() for _ in range(randint(2, 5))]
            for c in c_objs:
                self.db.setCollection(c)
            self.assertSetEqual(set([json.dumps(c) for c in c_objs]), set([json.dumps(c) for c in self.db.getCollections()]))

    def test_db_delete_created_collection(self):
        with app.app_context():
            c_obj = self.mock.collection()
            self.db.setCollection(c_obj)
            self.db.delCollection(c_obj.id)
            self.assertFalse(os.path.isfile(os.path.join(self.db.d_data, c_obj.id, self.db.d_collection)))

    def test_db_overwrite_collection(self):
        with app.app_context():
            c_obj = self.mock.collection()
            d_obj = self.mock.collection()
            d_obj.id = c_obj.id
            d_obj.capabilities.isOrdered = not c_obj.capabilities.isOrdered
            self.db.setCollection(c_obj)
            self.assertNotEqual(self.db.getCollections(c_obj.id)[0].capabilities.isOrdered, d_obj.capabilities.isOrdered)
            self.db.setCollection(d_obj)
            self.assertEqual(self.db.getCollections(c_obj.id)[0].capabilities.isOrdered, d_obj.capabilities.isOrdered)

    def test_db_create_member_on_filesystem(self):
        with app.app_context():
            c_obj = self.mock.collection()
            m_obj = self.mock.member()
            self.db.setCollection(c_obj)
            self.db.setMember(c_obj.id, m_obj)
            self.assertTrue(os.path.isfile(os.path.join(self.db.d_data, c_obj.id.replace('/', '∕'), m_obj.id.replace('/', '∕')+'.json')))

    def test_db_access_created_member(self):
        with app.app_context():
            c_obj = self.mock.collection()
            m_obj = self.mock.member()
            self.db.setCollection(c_obj)
            self.db.setMember(c_obj.id, m_obj)
            self.assertEqual(json.dumps(m_obj), json.dumps(self.db.getMembers(c_obj.id, m_obj.id).pop()))

    def test_db_access_multiple_members(self):
        with app.app_context():
            c_obj = self.mock.collection()
            self.db.setCollection(c_obj)
            m_objs = [self.mock.member() for _ in range(randint(2, 5))]
            for m_obj in m_objs:
                self.db.setMember(c_obj.id, m_obj)
            self.assertSetEqual(set([json.dumps(m) for m in m_objs]), set([json.dumps(m) for m in self.db.getMembers(c_obj.id)]))

    def test_db_delete_created_member(self):
        with app.app_context():
            c_obj = self.mock.collection()
            m_obj = self.mock.member()
            self.db.setCollection(c_obj)
            self.db.setMember(c_obj.id, m_obj)
            self.assertTrue(len(self.db.getMembers(c_obj.id, m_obj.id)) == 1)
            self.db.delMember(c_obj.id, m_obj)
            with self.assertRaises(FileNotFoundError) as context:
                self.db.getMembers(c_obj.id, m_obj.id)

    def test_db_overwrite_member(self):
        with app.app_context():
            c_obj = self.mock.collection()
            m_obj = self.mock.member()
            n_obj = self.mock.member()
            n_obj.id = m_obj.id
            n_obj.location = m_obj.location+"x"
            self.db.setCollection(c_obj)
            self.db.setMember(c_obj.id, m_obj)
            self.db.setMember(c_obj.id, n_obj)
            self.assertEqual(self.db.getMembers(c_obj.id, m_obj.id)[0].location, n_obj.location)

    def test_db_create_service_on_filesystem(self):
        with app.app_context():
            s_obj = self.mock.service()
            self.db.setService(s_obj)
            self.assertTrue(os.path.isfile(os.path.join(self.db.d_data, self.db.d_service)))

    def test_db_access_created_service(self):
        with app.app_context():
            s_obj = self.mock.service()
            self.db.setService(s_obj)
            t_obj = self.db.getService()
            self.assertEqual(json.dumps(s_obj), json.dumps(t_obj))

    def test_db_overwrite_service(self):
        with app.app_context():
            s_obj = self.mock.service()
            t_obj = self.mock.service()
            t_obj.providesCollectionPids = not s_obj.providesCollectionPids
            self.db.setService(s_obj)
            self.db.setService(t_obj)
            self.assertNotEqual(json.dumps(s_obj), json.dumps(self.db.getService()))

if __name__ == '__main__':
    main()
