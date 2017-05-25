from unittest import TestCase
from src.utils.access.null_control import NullACL
from src.utils.access.permissions import Permissions


class NullControlTest(TestCase):

    def setUp(self):
        self.control = NullACL()

    def test_get_permission(self):
        blank = self.control.get_permission()
        cid = self.control.get_permission(cID="")
        uid = self.control.get_permission(uID="")
        self.assertTrue(blank.r and blank.w and blank.x)
        self.assertTrue(cid.r and cid.w and cid.x)
        self.assertTrue(cid.r and cid.w and cid.x)

    def test_set_permission(self):
        self.assertFalse(self.control.set_permission(None))
        self.assertFalse(self.control.set_permission(Permissions()))
        self.assertFalse(self.control.set_permission(None, uID=""))
        with self.assertRaises(TypeError) as context:
            self.control.set_permission()


    def test_get_user(self):
        self.assertEqual(self.control.get_user(), 0)