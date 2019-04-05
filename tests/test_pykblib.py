"""PyKBLib Test Suite.

This test suite assumes that you've got Keybase running on your system. It also
assumes that a user is logged in.

This test suite also assumes the continued existence of the Keybase user known
as `pykblib` and the Keybase team called `pykblib_dev_team`, each of which was
created specifically for testing certain features of this suite. If this user
should ever get deleted, the testing suite will need to be modified
accordingly.

Before running this test suite, you'll need to create the 'dev_team.txt' file
if it doesn't already exist. Inside that file, write the name of a team you own
that you intend to use for testing.
"""

import random
import string
import sys
from unittest import TestCase

from pykblib import Keybase, Team

TEST_USER_NAME = "pykblib"
DEV_TEAM_NAME = "pykblib_dev_team.testing"


class KeybaseClassTest(TestCase):
    """Test the PyKBLib library."""

    @classmethod
    def setUpClass(cls):
        """Prepare the test suite for execution."""
        # Ensure that the user has created their dev_team.txt file.
        try:
            with open("dev_team.txt", "r") as f:
                test_team_name = f.readline().strip()
        except FileNotFoundError:
            print("I could not find the 'dev_team.txt' file, so I created it.")
            print("Please edit the file and replace 'TEAM_NAME' with your")
            print("development team's name. Then you can run unit tests.")
            with open("dev_team.txt", "w") as f:
                f.write("TEAM_NAME")
            sys.exit(0)
        # Connect to Keybase.
        keybase = Keybase()
        cls.keybase = keybase
        assert isinstance(
            cls.keybase, Keybase
        ), "Could not create keybase instance."
        # Leave the pykblib test team, if already a member.
        assert keybase.leave_team(
            DEV_TEAM_NAME
        ), "Could not leave dev test team."
        # Generate a random 16-character team name. (Keybase team names cannot
        # exceed 16 characters.) We'll assume the team doesn't already exist.
        random_team_name = (
            test_team_name
            + "."
            + "".join(
                [random.choice(string.ascii_lowercase) for _ in range(13)]
            )
        )
        cls.random_team_name = random_team_name
        # Create the test team.
        team = keybase.create_team(random_team_name)
        cls.test_team = team
        assert isinstance(
            cls.test_team, Team
        ), "Could not create team instance."
        # Join the test team.
        assert cls.test_team.add_member(
            keybase.username, "admin"
        ), "Failed to join test team."

    @classmethod
    def tearDownClass(cls):
        """Remove the last team that was created."""
        assert cls.keybase.delete_team(
            cls.random_team_name
        ), "Could not delete team '{}'".format(cls.random_team_name)

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
        # Attempt to join the dev test team.
        self.assertTrue(
            KeybaseClassTest.keybase.request_access(DEV_TEAM_NAME),
            "Could not request access to {}".format(DEV_TEAM_NAME),
        )
        # Ensure that list_requests returns a list.
        self.assertIsInstance(
            KeybaseClassTest.keybase.list_requests(),
            list,
            "Keybase.list_requests failed to return a list.",
        )
        # Attempt to ignore the test user's request to join our team.
        self.assertTrue(
            KeybaseClassTest.test_team.ignore_request(TEST_USER_NAME),
            "Could not ignore request by test user.",
        )
        requests = KeybaseClassTest.test_team.list_requests()
        self.assertIsInstance(
            requests, list, "Team.list_requests failed to return a list."
        )
        self.assertTrue(requests == [])
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
        # Attempt to leave the dev test team.
        self.assertTrue(
            KeybaseClassTest.keybase.leave_team(DEV_TEAM_NAME),
            "Could not leave dev test team.",
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
        sub_team = KeybaseClassTest.test_team.create_sub_team("sub1")
        self.assertIsInstance(sub_team, Team)
        # Attempt to create a sub-sub-team.
        sub_sub_team = sub_team.create_sub_team("subsub1")
        self.assertIsInstance(sub_sub_team, Team)
        # Attempt to create a second sub-sub-team.
        sub_sub_team2 = sub_team.create_sub_team("subsub2")
        self.assertIsInstance(sub_sub_team2, Team)
        # Attempt to rename the sub team.
        self.assertTrue(sub_team.rename("sub2"))
        # Ensure that the name was changed, both for the sub_team and for the
        # sub_sub_team.
        self.assertEqual(
            sub_team.name, KeybaseClassTest.random_team_name + "." + "sub2"
        )
        self.assertIn(sub_team.name, sub_sub_team.name)
        # Ensure that the new teams are in KeybaseClassTest.keybase.teams.
        self.assertIn(
            KeybaseClassTest.test_team.name, KeybaseClassTest.keybase.teams
        )
        self.assertIn(sub_team.name, KeybaseClassTest.keybase.teams)
        self.assertIn(sub_sub_team.name, KeybaseClassTest.keybase.teams)
        # Attempt to delete a bad team name.
        self.assertFalse(
            KeybaseClassTest.keybase.delete_team("; ls -la"),
            "Shouldn't be able to exploit delete_team.",
        )
        self.assertFalse(
            KeybaseClassTest.keybase.delete_team("not_a_real_team"),
            "Shouldn't be able to delete a team that doesn't exist.",
        )
        # Attempt to delete the second sub-sub-team.
        sub_sub2_name = sub_sub_team2.name
        self.assertTrue(
            KeybaseClassTest.keybase.delete_team(sub_sub2_name),
            "Couldn't delete second sub sub team.",
        )
        self.assertNotIn(sub_sub2_name, KeybaseClassTest.keybase.teams)
        # Ensure that deleting a team deletes all of its sub-teams.
        sub_name = sub_team.name
        sub_sub_name = sub_sub_team.name
        # This time we test with the Team.delete function.
        self.assertTrue(sub_team.delete(), "Couldn't delete sub team.")
        self.assertNotIn(sub_name, KeybaseClassTest.keybase.teams)
        self.assertNotIn(sub_sub_name, KeybaseClassTest.keybase.teams)
        # Ensure we can't create a new instance of the Keybase test team.
        with self.assertRaises(AssertionError):
            KeybaseClassTest.keybase.team(sub_name)
