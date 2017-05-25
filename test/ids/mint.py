from unittest import TestCase
from requests.exceptions import ConnectionError
from src.collections.models import CollectionObject, CollectionCapabilities
from src.members.models import MemberItem
from src.utils.ids.mint import *

class MintTest(TestCase):

    def test_urn_generator(self):
        mint = URNGenerator()
        mint.get_id(CollectionObject).startswith("urn:cite:collections.")
        mint.get_id(MemberItem).startswith("urn:cite:items.")
        with self.assertRaises(TypeError) as context:
            mint.get_id()
        with self.assertRaises(TypeError) as context:
            mint.get_id("MemberItem")
        with self.assertRaises(TypeError) as context:
            mint.get_id(CollectionCapabilities)

    def test_remote_generator(self):
        mint = RemoteGenerator("http://localhost/remote_generator_test/{}")
        with self.assertRaises(ConnectionError) as context:
            mint.get_id(CollectionObject)