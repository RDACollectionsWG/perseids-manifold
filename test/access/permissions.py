from unittest import TestCase
from src.utils.access.permissions import Permissions


class PermissionsTest(TestCase):

    def test_constrcutor(self):
        self.assertFalse(Permissions().r)
        self.assertFalse(Permissions().w)
        self.assertFalse(Permissions().x)
        self.assertFalse(Permissions(True,True).x)
        self.assertTrue(Permissions(True).r)
        self.assertTrue(Permissions(w=True).w)
        self.assertTrue(Permissions(x=True).x)
        with self.assertRaises(TypeError) as context:
            Permissions("string")
        with self.assertRaises(TypeError) as context:
            Permissions(1)
