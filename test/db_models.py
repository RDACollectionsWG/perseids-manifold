from unittest import TestCase

from flask import json

from src.collections.models import *
from src.members.models import *
from src.service.models import *

from .mock import RandomGenerator

from run import app

# can be created with kwargs
# can be created with dict
# can be created with or without id -> potentially mint ID in apply function
# is Model/Dictionary subclass
# can be serialized to JSON
# can be deserialized from JSON
# test for optional properties
# test behavior for missing / superfluous arguments

class ModelTests(TestCase):

    def setUp(self):
        self.mock = RandomGenerator()

    def test_models_create_collection_with_kwargs(self):
        c_obj = CollectionObject("", self.mock.collection().capabilities, self.mock.collection().properties, "")
        self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_collection_with_dict(self):
        c_obj = CollectionObject(**{
            'id': "",
            'capabilities': self.mock.collection().capabilities,
            'properties': self.mock.collection().properties,
            'description': ""
        })
        self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_collection_with_json(self):
        with app.app_context():
            c_obj = json.loads(self.mock.json_collection())
            self.assertEqual(type(c_obj), CollectionObject)
            self.assertEqual(type(c_obj.capabilities), CollectionCapabilities)
            self.assertEqual(type(c_obj.properties), CollectionProperties)

    def test_models_deserialize_collection_to_json(self):
        with app.app_context():
            c_str = self.mock.json_collection()
            c_obj = json.loads(c_str)
            self.assertEqual(c_str, json.dumps(c_obj))

    def test_models_collection_is_model(self):
        self.assertTrue(False)

    def test_models_collection_fails_with_superfluous_args(self):
        self.assertTrue(False)

    def test_models_create_member_with_kwargs(self):
            c_obj = CollectionObject("", self.mock.collection().capabilities, self.mock.collection().properties, "")
            self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_member_with_dict(self):
        c_obj = CollectionObject(**{
            'id': "",
            'capabilities': self.mock.collection().capabilities,
            'properties': self.mock.collection().properties,
            'description': ""
        })
        self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_member_with_json(self):
        self.assertTrue(False)

    def test_models_deserialize_member_to_json(self):
        self.assertTrue(False)

    def test_models_member_is_model(self):
        self.assertTrue(False)

    def test_models_member_fails_with_superfluous_args(self):
        self.assertTrue(False)

    def test_models_create_service_with_kwargs(self):
        c_obj = CollectionObject("", self.mock.collection().capabilities, self.mock.collection().properties, "")
        self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_service_with_dict(self):
        c_obj = CollectionObject(**{
            'id': "",
            'capabilities': self.mock.collection().capabilities,
            'properties': self.mock.collection().properties,
            'description': ""
        })
        self.assertEqual(type(c_obj), CollectionObject)

    def test_models_create_service_with_json(self):
        self.assertTrue(False)

    def test_models_deserialize_service_to_json(self):
        self.assertTrue(False)

    def test_models_service_is_model(self):
        self.assertTrue(False)

    def test_models_service_fails_with_superfluous_args(self):
        self.assertTrue(False)
