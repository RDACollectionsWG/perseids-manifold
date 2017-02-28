from src.data.db import DataBase
from unittest import TestCase, main
from tempfile import TemporaryDirectory
from random import randint
from run import app
from .mock import RandomGenerator
import os


class DbTests(TestCase):

    def setUp(self):
        self.dir = TemporaryDirectory(dir='./test/data')
        self.db = DataBase(self.dir.name)
        self.app = app
        self.mock = RandomGenerator()

    def tearDown(self):
        self.dir.cleanup()

    def test_db_create_collection_on_filesystem(self):
        with app.app_context():
            c_obj = self.mock.collection()
            self.db.setCollection(c_obj)
            self.assertTrue(os.path.isfile(os.path.join(self.db.d_data, c_obj.id, self.db.d_collection)))

    def test_db_access_created_collection(self):
        with app.app_context():
            c_obj = self.mock.collection
            self.db.setCollection(c_obj)
            self.assertDictEqual(c_obj.__dict__, self.db.getCollections(c_obj.id).pop().__dict__)

    def test_db_access_multiple_collections(self):
        with app.app_context():
            c_objs = [self.mock.collection() for _ in randint(2, 5)]
            for c in c_objs:
                self.db.setCollection(c)
            self.assertListEqual([c.__dict__ for c in c_objs], [c.__dict__ for c in self.db.getCollections()]) # todo: order? deep?

    def test_db_delete_created_collection(self):
        with app.app_context():
            self.db.setCollection(self.c_obj)
            self.db.delCollection(self.c_obj.id)
            self.assertFalse(os.path.isfile(os.path.join(self.db.d_data, self.c_obj.id, self.db.d_collection)))

if __name__ == '__main__':
    main()
