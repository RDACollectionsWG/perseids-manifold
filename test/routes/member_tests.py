import urllib
from tempfile import TemporaryDirectory
from unittest import TestCase

from flask import json

from run import app
from src.utils.base.errors import NotFoundError
from src.utils.data.filesystem_db import FilesystemDB
from test.mock import RandomGenerator


class MembersTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n>> Test Members Routes >>>>>>>>>>>>>>>>>")

    def setUp(self):
        self.app = app
        self.dir = TemporaryDirectory(dir='test/data')
        self.app.db = FilesystemDB(self.dir.name)
        self.mock = RandomGenerator()

    def tearDown(self):
        self.dir.cleanup()

    def get(self, path):
        with self.app.test_client() as client:
            return client.get(path, follow_redirects=True)

    def post(self, path, data):
        with self.app.test_client() as client:
            return client.post(path, data=data, follow_redirects=True)

    def put(self, path, data):
        with self.app.test_client() as client:
            return client.put(path, data=data, follow_redirects=True)

    def delete(self, path):
        with self.app.test_client() as client:
            return client.delete(path, follow_redirects=True)

    def test_members_get_id(self):
        with self.app.app_context():
            # create collection, members
            c_obj = self.mock.collection()
            m_objs = [self.mock.member() for i in range(5)]
            # add collection, members
            self.app.db.set_collection(c_obj)
            for m_obj in m_objs:
                self.app.db.set_member(c_obj.id, m_obj)
            # GET members
            responses = [{'out': self.get("collections/"+urllib.parse.quote_plus(c_obj.id)+"/members/"+urllib.parse.quote_plus(m_obj.id)), 'in':m_obj} for m_obj in m_objs]
            # assert 200 OK
            for r in responses:
                self.assertEqual(r['out'].status_code, 200)
                # compare members
                self.assertDictEqual(json.loads(r['out'].data).__dict__, r['in'].__dict__)

    def test_members_get(self):
        with self.app.app_context():
            # create collection, members
            c_obj = self.mock.collection()
            m_objs = [self.mock.member() for i in range(5)]
            # add collection, members
            self.app.db.set_collection(c_obj)
            for m_obj in m_objs:
                self.app.db.set_member(c_obj.id, m_obj)
            # GET members
            response = self.get("collections/"+urllib.parse.quote_plus(c_obj.id)+"/members")
            # assert 200 OK
            self.assertEqual(response.status_code, 200)
            sortedResponse = [r.__dict__ for r in sorted(json.loads(response.data)['contents'], key=lambda x: x.id)]
            sortedMocks = [m.__dict__ for m in sorted(m_objs, key=lambda x: x.id)]
            for i in range(len(sortedMocks)):
                self.assertDictEqual(sortedResponse[i], sortedMocks[i])

    def test_members_post(self):
        with self.app.app_context():
            c_obj = self.mock.collection()
            self.app.db.set_collection(c_obj)
            m_dicts = [self.mock.member().__dict__ for i in range(5)]
            self.assertListEqual(self.app.db.get_member(c_obj.id), [])
            responses = [self.post("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members", json.dumps(m)) for m in m_dicts]
            for r in responses:
                self.assertEqual(r.status_code, 201)
            sortedResponse = sorted([json.loads(response.data).pop() for response in responses], key=lambda x: x.location)
            sortedMocks = sorted(m_dicts, key=lambda x: x['location'])
            for i in range(len(sortedMocks)):
                self.assertEqual(sortedMocks[i]['location'], sortedResponse[i].location)

    def test_members_put_id(self):
        with self.app.app_context():
            c_obj = self.mock.collection()
            self.app.db.set_collection(c_obj)
            m_objs = [self.mock.member() for i in range(5)]
            for m_obj in m_objs:
                self.app.db.set_member(c_obj.id, m_obj)
            for m_obj in m_objs:
                m_dict = {'id':m_obj.id, 'location': m_obj.location+"-changed"}
                response = self.put("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members/"+urllib.parse.quote_plus(m_obj.id), json.dumps(m_dict))
                result = json.loads(response.data)['contents'][0]
                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(result.__dict__, m_dict)
                self.assertEqual(m_obj.id, result.id)
                self.assertNotEqual(m_obj.location, result.location)


    def test_members_delete_id(self):
        with self.app.app_context():
            c_obj = self.mock.collection()
            self.app.db.set_collection(c_obj)
            m_objs = [self.mock.member() for i in range(5)]
            for m_obj in m_objs:
                self.app.db.set_member(c_obj.id, m_obj)
                response = self.delete("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members/"+urllib.parse.quote_plus(m_obj.id))
                self.assertEqual(response.status_code, 200)
                with self.assertRaises(NotFoundError):
                    self.app.db.get_member(c_obj.id, m_obj.id)

    def test_members_delete_unknown_id(self):
        with self.app.app_context():
            c_obj = self.mock.collection()
            self.app.db.set_collection(c_obj)
            m_obj = self.mock.member()
            response = self.delete("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members/"+urllib.parse.quote_plus(m_obj.id))
            self.assertEqual(response.status_code, 404)
