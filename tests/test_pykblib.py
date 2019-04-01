"""PyKBLib Test Suite.

This test suite assumes that you've got Keybase running on your system. It also
assumes that you're logged in, and that the active user is an admin of the
`pykblib_dev` team. (This is an open team, so all are free to join, but only
users known to be contributing to the development of this library will be given
admin status.)

This test suite also assumes the continued existence of the Keybase user known
as `pykblib`, which was created specifically for testing certain features of
this suite. If this user should ever get deleted, the testing suite will need
to be modified accordingly.
"""

import random
import string
from unittest import TestCase

from pykblib import Keybase, Team


DEV_TEAM_NAME = "pykblib_dev"
TEST_USER_NAME = "pykblib"


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
        # Ensure that the teams attribute is a list.
        self.assertIsInstance(self.keybase.teams, list)
        # Ensure that the user is a member of the `pykblib_dev` team.
        self.assertIn(DEV_TEAM_NAME, self.keybase.teams)

    def test_keybase_team_class(self):
        """Ensure that the team class is working properly.

        Note: Some methods could not be automatically tested due to dependence
        on the Keybase application. For example, the purge_deleted method needs
        to be tested in a server where users have joined a team and then
        deleted their accounts. This is not something easily automated with a
        unit test.
        """
        # Retrieve an instance of the dev team's Team class.
        dev_team = self.keybase.team(DEV_TEAM_NAME)
        # Ensure that the dev_team variable is a Team.
        self.assertIsInstance(dev_team, Team)
        # Ensure that the team name attribute is a string.
        self.assertIsInstance(dev_team.name, str)
        # Ensure that the team name is DEV_TEAM_NAME.
        self.assertEqual(dev_team.name, DEV_TEAM_NAME)
        # Ensure that the team roles attribute is a list.
        self.assertIsInstance(dev_team.role, str)
        # Ensure that the team member_count attribute is an int.
        self.assertIsInstance(dev_team.member_count, int)
        # Ensure that the members list is a list.
        self.assertIsInstance(dev_team.members, list)
        # Ensure that the owners list is a list.
        self.assertIsInstance(dev_team.members_by_role.owner, list)
        # Ensure that the admins list is a list.
        self.assertIsInstance(dev_team.members_by_role.admin, list)
        # Ensure that the writers list is a list.
        self.assertIsInstance(dev_team.members_by_role.writer, list)
        # Ensure that the readers list is a list.
        self.assertIsInstance(dev_team.members_by_role.reader, list)
        # Ensure that the deleted list is a list.
        self.assertIsInstance(dev_team.deleted, list)
        # Ensure that the members list contains the number of members specified
        # in the member_count.
        self.assertEqual(len(dev_team.members), dev_team.member_count)
        # Ensure that the active user is in the members list.
        self.assertIn(self.keybase.username, dev_team.members)
        # Ensure that the active user is an owner or admin of the team.
        self.assertTrue(
            self.keybase.username
            in dev_team.members_by_role.owner + dev_team.members_by_role.admin
        )

    def test_keybase_team_member_mgmt(self):
        """Check whether team member management is working properly."""
        # Retrieve an instance of the dev team's Team class.
        dev_team = self.keybase.team(DEV_TEAM_NAME)
        # Attempt to remove the 'pykblib' user from the team, in preparation
        # for the next section. This requires admin privileges in the team.
        dev_team.remove_member(TEST_USER_NAME)
        # Attempt to add the test user to the team as a reader.
        self.assertEqual(dev_team.add_member(TEST_USER_NAME), True)
        # Attempt to remove the test user from the team.
        self.assertEqual(dev_team.remove_member(TEST_USER_NAME), True)
        # Attempt to add the test user to the team as a writer.
        self.assertEqual(dev_team.add_member(TEST_USER_NAME, "writer"), True)
        # Attempt to change the test user's role to "reader".
        self.assertEqual(
            dev_team.change_member_role(TEST_USER_NAME, "reader"), True
        )
        # Attempt to remove the test user from the team.
        self.assertEqual(dev_team.remove_member(TEST_USER_NAME), True)
        # Generate a random 16-character username. (Keybase usernames cannot
        # exceed 16 characters.) We'll assume that they don't exist.
        fake_user = "demo_" + "".join(
            [random.choice(string.ascii_letters) for _ in range(11)]
        )
        # Attempt to add the fake user to the team.
        self.assertEqual(dev_team.add_member(fake_user), False)
        # Attempt to remove the fake user from the team.
        self.assertEqual(dev_team.remove_member(fake_user), False)
