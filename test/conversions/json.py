from unittest import TestCase
from src.utils.base.models import Model
from src.utils.conversions.json import RDAJSONDecoder, RDAJSONEncoder
from test.mock import RandomGenerator

class JSONTest(TestCase):

    def setUp(self):
        self.mock = RandomGenerator()

    def test_decode(self):
        decoder = RDAJSONDecoder()
        json = self.mock.json_collection()
        obj = decoder.decode(json)
        self.assertIsInstance(obj, Model)
        self.assertIsInstance(obj.capabilities, Model)
        self.assertIsInstance(obj.properties, Model)

    def test_encode(self):
        encoder = RDAJSONEncoder()
        obj = self.mock.collection()
        dct = encoder.default(obj)
        self.assertIsInstance(dct, dict)
        self.assertIsInstance(dct.get('capabilities'), dict)
        self.assertIsInstance(dct.get('properties'), dict)
        self.assertDictEqual(dct, obj.dict())
