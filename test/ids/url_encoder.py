import random, string
from unittest import TestCase
from src.utils.ids.url_encoder import encoder

class URLEncoderTest(TestCase):

    def test_encode_round(self):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))
        binary = encoder.encode(text)
        result = encoder.decode(binary)
        self.assertEqual(text, result)

    def test_encoder_input(self):
        with self.assertRaises(TypeError) as context:
            encoder.encode(1000)
        with self.assertRaises(TypeError) as context:
            encoder.decode(1111)
