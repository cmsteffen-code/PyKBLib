from unittest import TestCase

from pykblib.exceptions import KBLibException


class KeybaseExceptionTest(TestCase):
    def test_exception(self):
        with self.assertRaises(KBLibException) as raised:
            raise KBLibException("test message")
        self.assertEqual(raised.exception.message, "test message")
