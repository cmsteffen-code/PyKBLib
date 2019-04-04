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
        # Ensure that the members function returns a list.
        self.assertIsInstance(dev_team.members(), list)
        # Ensure that the owners list is a list.
        self.assertIsInstance(dev_team.members_by_role.owner, list)
        # Ensure that the admins list is a list.
        self.assertIsInstance(dev_team.members_by_role.admin, list)
        # Ensure that the writers list is a list.
        self.assertIsInstance(dev_team.members_by_role.writer, list)
        # Ensure that the readers list is a list.
        self.assertIsInstance(dev_team.members_by_role.reader, list)
        # Ensure that the deleted list is a list.
        self.assertIsInstance(dev_team.members_by_role.deleted, list)
        # Ensure that the reset list is a list.
        self.assertIsInstance(dev_team.members_by_role.reset, list)
        # Ensure that the active user is in the members list.
        self.assertIn(self.keybase.username, dev_team.members())
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
        # Attempt to add the test user to the team as a writer.
        self.assertEqual(dev_team.add_member(TEST_USER_NAME, "writer"), True)
        self.assertIn(TEST_USER_NAME, dev_team.members_by_role.writer)
        # Attempt to add the user again.
        self.assertEqual(dev_team.add_member(TEST_USER_NAME), False)
        # Attempt to change the test user's role to "reader".
        self.assertEqual(
            dev_team.change_member_role(TEST_USER_NAME, "reader"), True
        )
        self.assertIn(TEST_USER_NAME, dev_team.members_by_role.reader)
        self.assertNotIn(TEST_USER_NAME, dev_team.members_by_role.writer)
        # Attempt to remove the test user from the team.
        self.assertEqual(dev_team.remove_member(TEST_USER_NAME), True)
        self.assertNotIn(TEST_USER_NAME, dev_team.members_by_role.reader)
        # Generate a random 16-character username. (Keybase usernames cannot
        # exceed 16 characters.) We'll assume that they don't exist.
        fake_user = "demo_" + "".join(
            [random.choice(string.ascii_letters) for _ in range(11)]
        )
        # Attempt to add the fake user to the team.
        self.assertEqual(dev_team.add_member(fake_user), False)
        self.assertNotIn(fake_user, dev_team.members_by_role.reader)
        # Attempt to remove the fake user from the team.
        self.assertEqual(dev_team.remove_member(fake_user), False)

    def test_keybase_team_management(self):
        """Check whether the team management is working properly."""
        # Generate a random 16-character team name. (Keybase team names cannot
        # exceed 16 characters.) We'll assume the team doesn't already exist.
        random_team_name = "team_" + "".join(
            [
                random.choice(string.ascii_lowercase + string.digits + "_-")
                for _ in range(11)
            ]
        )
        # Attempt to create the new team.
        test_team = self.keybase.create_team(random_team_name)
        self.assertIsInstance(test_team, Team)
        # Ensure that creating the team a second time fails.
        self.assertFalse(self.keybase.create_team(random_team_name))
        # Attempt to create a sub-team.
        sub_team = test_team.create_sub_team("subteam")
        self.assertIsInstance(sub_team, Team)
        # Attempt to rename the main team.
        self.assertFalse(test_team.rename("this_should_fail"))
        self.assertEqual(test_team.name, random_team_name)
        # Attempt to rename the sub team.
        self.assertTrue(sub_team.rename("subteam2"))
        self.assertEqual(sub_team.name, random_team_name + "." + "subteam2")
        # Ensure that the new teams are in the self.keybase.teams list.
        self.assertIn(test_team.name, self.keybase.teams)
        self.assertIn(sub_team.name, self.keybase.teams)
        # For now we don't have a reliable way to delete teams, so we have to
        # do it manually.
        print("\nPlease remember to delete test teams:")
        print("* {}".format(test_team.name))
        print("* {}".format(sub_team.name))
