"""PyKBLib Test Suite.

This test suite assumes that you've got Keybase running on your system. It also
assumes that you're logged in, and that the active user is a member of the
`pykblib_dev` team. (This is an open team, so all are free to join.)
"""

from unittest import TestCase

from pykblib import Keybase, Team


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

    def test_keybase_teams(self):
        """Ensure that keybase.teams attribute is working properly."""
        # Ensure that the teams attribute is a list.
        self.assertIsInstance(self.keybase.teams, list)
        # Ensure that the user is a member of the `pykblib_dev` team.
        self.assertIn("pykblib_dev", self.keybase.teams)

    def test_keybase_team_class(self):
        """Ensure that the team class is working properly."""
        # Retrieve an instance of the dev team's Team class.
        dev_team = self.keybase.team("pykblib_dev")
        # Ensure that the dev_team variable is a Team.
        self.assertIsInstance(dev_team, Team)
        # Ensure that the team name attribute is a string.
        self.assertIsInstance(dev_team.name, str)
        # Ensure that the team name is "pykblib_dev".
        self.assertEqual(dev_team.name, "pykblib_dev")
        # Ensure that the team roles attribute is a list.
        self.assertIsInstance(dev_team.roles, list)
        # Ensure that the team member_count attribute is an int.
        self.assertIsInstance(dev_team.member_count, int)
