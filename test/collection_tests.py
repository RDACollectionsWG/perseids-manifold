from unittest import TestCase, main
from tempfile import TemporaryDirectory, mkdtemp
from run import app
from src.data.filesystem_db import FilesystemDB
from .mock import RandomGenerator
from flask import json
from src.collections.models import CollectionObject
import urllib


class CollectionTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n>> Test Collections Routes >>>>>>>>>>>>>")

    def setUp(self):
        self.app = app
        self.dir = TemporaryDirectory(dir='test/data')
        # self.dir = mkdtemp(dir='test/data')
        self.app.db = FilesystemDB(self.dir.name)
        self.mock = RandomGenerator()

    def tearDown(self):
        self.dir.cleanup()

    def to_dict(self, c_obj):
        if isinstance(c_obj, CollectionObject):
            c_dict = c_obj.__dict__
            c_dict['capabilities'] = c_dict['capabilities'].__dict__
            c_dict['properties'] = c_dict['properties'].__dict__
            return c_dict

    def get(self, path):
        with self.app.test_client() as client:
            return client.get(path, follow_redirects=True)

    def test_collection_get(self):
        with self.app.app_context():
            c_objs = [self.mock.collection() for i in range(5)]
            for c in c_objs:
                self.app.db.set_collection(c)
            response = self.get("/collections")
            loaded = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertListEqual([json.dumps(c) for c in sorted(loaded['contents'], key=lambda x: x.id)], [json.dumps(c) for c in sorted(c_objs, key=lambda x: x.id)])

    def test_collection_get_id(self):
        with self.app.app_context():
            c_objs = [self.mock.collection() for i in range(5)]
            for c in c_objs:
                self.app.db.set_collection(c)
            response = [self.get("/collections/"+urllib.parse.quote_plus(c.id)) for c in c_objs]
            loaded = [json.loads(r.data) for r in response]
            for r in response:
                self.assertEqual(r.status_code, 200)
            self.assertListEqual([json.dumps(c) for c in sorted([c_obj for resultset in loaded for c_obj in resultset['contents']], key=lambda x: x.id)], [json.dumps(c) for c in sorted(c_objs, key=lambda x: x.id)])

    def test_collection_get_unknown_id(self):
        response = self.get("/collections/ubifdnoi3hrfiu")
        self.assertEqual(response.status_code, 404)

    def test_collection_post(self):
        with self.app.app_context():
            c_dicts = [self.mock.collection().__dict__ for i in range(5)]
            for d in c_dicts:
                del d['id']
            with self.app.test_client() as c:
                results = [{'out': c.post("/collections", data=json.dumps(col), content_type='application/json', follow_redirects=True), 'in': col} for col in c_dicts]
            for r in results:
                self.assertEqual(r['out'].status_code, 201)
                r_dict = json.loads(r['out'].data).__dict__
                self.assertIsInstance(r_dict['id'], str)
                del r_dict['id']
                self.assertEqual(json.dumps(r_dict), json.dumps(r['in']))

    def test_collection_delete_id(self):
        with self.app.app_context():
            c_objs = [self.mock.collection() for i in range(5)]
            for c in c_objs:
                self.app.db.set_collection(c)
            with self.app.test_client() as c:
                results = [c.delete("/collections/"+urllib.parse.quote_plus(col.id), follow_redirects=True) for col in c_objs]
            for r in results:
                self.assertEqual(r.status_code, 200)
            for c in c_objs:
                with self.assertRaises(FileNotFoundError):
                    self.app.db.get_collection(c.id)

    def test_collection_delete_unknown_id(self):
        with self.app.test_client() as c:
            response = c.delete("/collections/tgvfrde", follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_collection_put_id(self):
        with self.app.app_context():
            c_objs = [self.mock.collection() for i in range(5)]
            for c in c_objs:
                self.app.db.set_collection(c)
                c.description = c.description+"changed"
            with self.app.test_client() as c:
                for col in c_objs:
                    response = c.put("/collections/"+urllib.parse.quote_plus(col.id), data=json.dumps(col), content_type="application/json", follow_redirects=True)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(json.dumps(json.loads(response.data)), json.dumps(col))
                    response = self.get("/collections/"+urllib.parse.quote_plus(col.id))
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(json.dumps(json.loads(response.data)['contents'][0]), json.dumps(col))

    def test_collection_put_unknown_id(self):
        with self.app.app_context():
            c_obj = self.mock.collection()
            with self.app.test_client() as c:
                response = c.put("/collections/"+urllib.parse.quote_plus(c_obj.id), data=json.dumps(c_obj), content_type="application/json", follow_redirects=True)
                self.assertEqual(response.status_code, 404)

