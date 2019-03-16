"""PyKBLib Test Suite.

This test suite assumes that you've got Keybase running on your system.
"""

from unittest import TestCase

from pykblib import Keybase


class KeybaseClassTest(TestCase):
    """Test the Keybase class."""
    def setUp(self):
        """Instantiate a new Keybase object."""
        self.keybase = Keybase()

    def test_keybase_class(self):
        """Perform basic tests on the Keybase class."""
        # Make sure self.keybase is a Keybase instance.
        self.assertIsInstance(self.keybase, Keybase)
        # Ensure that the username is a string.
        self.assertIsInstance(self.keybase.username, str)
        # Ensure that the username is properly retrieved.
        self.assertNotEqual(self.keybase.username, "")
