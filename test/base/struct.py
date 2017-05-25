from unittest import TestCase
from src.utils.base.struct import Struct

class StructTest(TestCase):

    def test_struct(self):
        struct = Struct(a="a", b=3, c=None, d={'a':12})
        self.assertEqual(struct.a, "a")
        self.assertEqual(struct.b, 3)
        self.assertEqual(struct.c, None)
        self.assertEqual(struct.d, {'a': 12})
