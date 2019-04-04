"""PyKBLib Test Suite.

This test suite assumes that you've got Keybase running on your system. It also
assumes that a user is logged in.

This test suite also assumes the continued existence of the Keybase user known
as `pykblib`, which was created specifically for testing certain features of
this suite. If this user should ever get deleted, the testing suite will need
to be modified accordingly.
"""

import random
import string
from unittest import TestCase

from pykblib import Keybase, Team

TEST_USER_NAME = "pykblib"


class KeybaseClassTest(TestCase):
    """Test the PyKBLib library."""

    @classmethod
    def setUpClass(cls):
        """Prepare the test suite for execution."""
        KB = Keybase()
        cls.keybase = KB
        assert isinstance(
            cls.keybase, Keybase
        ), "Could not create keybase instance. Please try again."
        # Generate a random 16-character team name. (Keybase team names cannot
        # exceed 16 characters.) We'll assume the team doesn't already exist.
        random_team_name = "team_" + "".join(
            [
                random.choice(string.ascii_lowercase + string.digits + "_-")
                for _ in range(11)
            ]
        )
        cls.random_team_name = random_team_name
        # Create the test team.
        TEAM = KB.create_team(random_team_name)
        cls.test_team = TEAM
        assert isinstance(
            cls.test_team, Team
        ), "Could not create team instance. Please try again."

    def test_keybase_class(self):
        """Perform basic tests on the Keybase class."""
        # Make sure KeybaseClassTest.keybase is a Keybase instance.
        self.assertIsInstance(KeybaseClassTest.keybase, Keybase)
        # Ensure that the username is a string.
        self.assertIsInstance(KeybaseClassTest.keybase.username, str)
        # Ensure that the username is properly retrieved.
        self.assertNotEqual(KeybaseClassTest.keybase.username, "")
        # Ensure that the teams attribute is a list.
        self.assertIsInstance(KeybaseClassTest.keybase.teams, list)

    def test_team_class(self):
        """Ensure that the team class is working properly.

        Note: Some methods could not be automatically tested due to dependence
        on the Keybase application. For example, the purge_deleted method needs
        to be tested in a server where users have joined a team and then
        deleted their accounts. This is not something easily automated with a
        unit test.
        """
        # Ensure that the KeybaseClassTest.test_team variable is a Team.
        self.assertIsInstance(KeybaseClassTest.test_team, Team)
        # Ensure that the team name attribute is a string.
        self.assertIsInstance(KeybaseClassTest.test_team.name, str)
        # Ensure that the team name is KeybaseClassTest.random_team_name.
        self.assertEqual(
            KeybaseClassTest.test_team.name, KeybaseClassTest.random_team_name
        )
        # Ensure that the team roles attribute is a list.
        self.assertIsInstance(KeybaseClassTest.test_team.role, str)
        # Ensure that the members function returns a list.
        self.assertIsInstance(KeybaseClassTest.test_team.members(), list)
        # Ensure that the owners list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.owner, list
        )
        # Ensure that the admins list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.admin, list
        )
        # Ensure that the writers list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.writer, list
        )
        # Ensure that the readers list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.reader, list
        )
        # Ensure that the deleted list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.deleted, list
        )
        # Ensure that the reset list is a list.
        self.assertIsInstance(
            KeybaseClassTest.test_team.members_by_role.reset, list
        )
        # Ensure that the active user is in the members list.
        self.assertIn(
            KeybaseClassTest.keybase.username,
            KeybaseClassTest.test_team.members(),
        )
        # Ensure that the active user is an owner or admin of the team.
        self.assertTrue(
            KeybaseClassTest.keybase.username
            in KeybaseClassTest.test_team.members_by_role.owner
            + KeybaseClassTest.test_team.members_by_role.admin
        )

    def test_team_member_management(self):
        """Check whether team member management is working properly."""
        # Ensure that the KeybaseClassTest.test_team variable is a Team.
        self.assertIsInstance(KeybaseClassTest.test_team, Team)
        # Attempt to add the test user to the team as a writer.
        self.assertEqual(
            KeybaseClassTest.test_team.add_member(TEST_USER_NAME, "writer"),
            True,
        )
        self.assertIn(
            TEST_USER_NAME, KeybaseClassTest.test_team.members_by_role.writer
        )
        # Attempt to add the user again.
        self.assertEqual(
            KeybaseClassTest.test_team.add_member(TEST_USER_NAME), False
        )
        # Attempt to change the test user's role to "reader".
        self.assertEqual(
            KeybaseClassTest.test_team.change_member_role(
                TEST_USER_NAME, "reader"
            ),
            True,
        )
        self.assertIn(
            TEST_USER_NAME, KeybaseClassTest.test_team.members_by_role.reader
        )
        self.assertNotIn(
            TEST_USER_NAME, KeybaseClassTest.test_team.members_by_role.writer
        )
        # Attempt to remove the test user from the team.
        self.assertEqual(
            KeybaseClassTest.test_team.remove_member(TEST_USER_NAME), True
        )
        self.assertNotIn(
            TEST_USER_NAME, KeybaseClassTest.test_team.members_by_role.reader
        )
        # Generate a random 16-character username. (Keybase usernames cannot
        # exceed 16 characters.) We'll assume that they don't exist.
        fake_user = "demo_" + "".join(
            [random.choice(string.ascii_letters) for _ in range(11)]
        )
        # Attempt to add the fake user to the team.
        self.assertEqual(
            KeybaseClassTest.test_team.add_member(fake_user), False
        )
        self.assertNotIn(
            fake_user, KeybaseClassTest.test_team.members_by_role.reader
        )
        # Attempt to remove the fake user from the team.
        self.assertEqual(
            KeybaseClassTest.test_team.remove_member(fake_user), False
        )

    def test_team_management(self):
        """Check whether the team management is working properly."""
        # Ensure that the KeybaseClassTest.test_team variable is a Team.
        self.assertIsInstance(KeybaseClassTest.test_team, Team)
        # Ensure that creating the team a second time fails.
        self.assertFalse(
            KeybaseClassTest.keybase.create_team(
                KeybaseClassTest.random_team_name
            )
        )
        # Attempt to create a sub-team.
        sub_team = KeybaseClassTest.test_team.create_sub_team("subteam")
        self.assertIsInstance(sub_team, Team)
        # Attempt to create a sub-sub-team.
        sub_sub_team = sub_team.create_sub_team("subteam")
        self.assertIsInstance(sub_sub_team, Team)
        # Attempt to rename the main team.
        self.assertFalse(KeybaseClassTest.test_team.rename("this_should_fail"))
        self.assertEqual(
            KeybaseClassTest.test_team.name, KeybaseClassTest.random_team_name
        )
        # Attempt to rename the sub team.
        self.assertTrue(sub_team.rename("subteam2"))
        # Ensure that the name was changed, both for the sub_team and for the
        # sub_sub_team.
        self.assertEqual(
            sub_team.name, KeybaseClassTest.random_team_name + "." + "subteam2"
        )
        self.assertIn(sub_team.name, sub_sub_team.name)
        # Ensure that the new teams are in the KeybaseClassTest.keybase.teams list.
        self.assertIn(
            KeybaseClassTest.test_team.name, KeybaseClassTest.keybase.teams
        )
        self.assertIn(sub_team.name, KeybaseClassTest.keybase.teams)
        self.assertIn(sub_sub_team.name, KeybaseClassTest.keybase.teams)
        # For now we don't have a reliable way to delete teams, so we have to
        # do it manually.
        print("\nPlease remember to delete test teams:")
        print("* {}".format(KeybaseClassTest.test_team.name))
        print("* {}".format(sub_team.name))
        print("* {}".format(sub_sub_team.name))
