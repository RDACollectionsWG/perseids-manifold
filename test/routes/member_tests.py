import urllib, time, os, requests
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from flask import json
from multiprocessing.pool import ThreadPool

from run import app
from src.members.models import MemberItem
from src.utils.base.errors import NotFoundError
from src.utils.data.filesystem_db import FilesystemDB
from src.utils.data.ldp_db import LDPDataBase
from src.utils.rdf.queries import reset_marmotta
from test.mock import RandomGenerator


class MembersTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n>> Test Members Routes >>>>>>>>>>>>>>>>>")

    def setUp(self):
        self.app = app
        self.server = os.environ.get('COLLECTIONS_API_TEST_DB')
        if not self.server:
            raise EnvironmentError
        self.app.db = LDPDataBase(self.server)
        requests.post(self.app.db.marmotta.sparql.update, data=reset_marmotta, headers={"Content-Type":"application/sparql-update; charset=utf-8"})
        #elf.dir = TemporaryDirectory(dir='test/data')
        #elf.app.db = FilesystemDB(self.dir.name)
        self.mock = RandomGenerator()

    def tearDown(self):
        #elf.dir.cleanup()
        requests.post(self.app.db.marmotta.sparql.update, data=reset_marmotta, headers={"Content-Type":"application/sparql-update; charset=utf-8"})

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
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
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
                self.assertDictEqual(json.loads(r['out'].data).dict(), r['in'].dict())

    def test_members_get(self):
        with self.app.app_context():
            # create collection, members
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
            m_objs = [self.mock.member() for i in range(5)]
            # add collection, members
            self.app.db.set_collection(c_obj)
            # for m_obj in m_objs:
            self.app.db.set_member(c_obj.id, m_objs)
            # pool = ThreadPool(50)
            # pool.map(lambda m_obj: self.app.db.set_member(c_obj.id, m_obj), m_objs)
            # GET members
            response = self.get("collections/"+urllib.parse.quote_plus(c_obj.id)+"/members")
            # assert 200 OK
            self.assertEqual(response.status_code, 200)
            sortedResponse = [r.dict() for r in sorted(json.loads(response.data)['contents'], key=lambda x: x.id)]
            sortedMocks = [m.dict() for m in sorted(m_objs, key=lambda x: x.id)]
            for i in range(len(sortedMocks)):
                self.assertDictEqual(sortedResponse[i], sortedMocks[i])

    def test_member_recursive_get(self):
        with self.app.app_context():
            # create collection, members
            c_objs = [self.mock.collection(description={'something':'abcdefghi123ö'}) for i in range(5)]
            m_objs = {}
            for i in [0,1,2,3]:
                m_objs.update({c_objs[i].id:[self.mock.member() for j in range(4)]+[self.mock.member(c_objs[i+1].id)]})
            m_objs.update({c_objs[4].id: [self.mock.member() for i in range(5)]})
            # add collection, members
            for c_obj in c_objs:
                self.app.db.set_collection(c_obj)
            for c,ms in m_objs.items():
                for m in ms:
                    self.app.db.set_member(c, m)
            # GET members
            response = self.get("collections/"+urllib.parse.quote_plus(c_objs[0].id)+"/members?expandDepth=5")
            # assert 200 OK
            self.assertEqual(response.status_code, 200)
            dct = json.loads(response.data)
            #rint(response.data)
            for i in range(4):
                resultset = [d for d in dct.get('contents') if not isinstance(d, MemberItem)]
                self.assertEqual(len(resultset),1)
                dct = resultset[0]
            resultset = [d for d in dct.get('contents') if not isinstance(d, MemberItem)]
            self.assertEqual(len(resultset),0)

    def test_members_post(self):
        with self.app.app_context():
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
            self.app.db.set_collection(c_obj)
            m_dicts = [self.mock.member().dict() for i in range(5)]
            self.assertListEqual(self.app.db.get_member(c_obj.id), [])

            responses = [self.post("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members", json.dumps(m)) for m in m_dicts]
            for r in responses:
                self.assertEqual(r.status_code, 201)
            sortedResponse = sorted([json.loads(response.data).pop() for response in responses], key=lambda x: x.location)
            sortedMocks = sorted(m_dicts, key=lambda x: x['location'])
            for i in range(len(sortedMocks)):
                self.assertEqual(sortedMocks[i]['location'], sortedResponse[i].location)

    def test_members_post_array(self):
        with self.app.app_context():
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
            self.app.db.set_collection(c_obj)
            m_dicts = [self.mock.member().dict() for i in range(5)]
            self.assertListEqual(self.app.db.get_member(c_obj.id), [])
            response = self.post("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members", json.dumps(m_dicts))
            self.assertEqual(response.status_code, 201)
            sortedResponse = sorted(json.loads(response.data), key=lambda x: x.location)
            sortedMocks = sorted(m_dicts, key=lambda x: x['location'])
            for i in range(len(sortedMocks)):
                self.assertEqual(sortedMocks[i]['location'], sortedResponse[i].location)

    def test_members_post_too_many(self):
        with self.app.app_context():
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
            c_obj.capabilities.maxLength = 3
            self.app.db.set_collection(c_obj)
            m_dicts = [self.mock.member().__dict__ for i in range(5)]
            responses = [self.post("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members", json.dumps(m)) for m in m_dicts]
            self.assertListEqual([*map(lambda r:r.status_code,responses)], [201, 201, 201, 403, 403])

    def test_members_put_id(self):
        with self.app.app_context():
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
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
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
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
            c_obj = self.mock.collection(description={'something':'abcdefghi123ö'})
            self.app.db.set_collection(c_obj)
            m_obj = self.mock.member()
            response = self.delete("/collections/"+urllib.parse.quote_plus(c_obj.id)+"/members/"+urllib.parse.quote_plus(m_obj.id))
            self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    main()
