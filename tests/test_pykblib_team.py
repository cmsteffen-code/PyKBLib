"""Test the PyKBLib Team class."""

import random
from unittest import TestCase, mock

from steffentools import dict_to_ntuple

from pykblib.exceptions import APIException, KeybaseException, TeamException
from pykblib.team import Team


def random_username():
    return "".join(
        [random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10)]
    )


def random_role():
    return random.choice(["owner", "admin", "writer", "reader"])


class TeamInitializationTest(TestCase):
    @mock.patch("pykblib.team.KeybaseAPI")
    @mock.patch("pykblib.team.Team.update")
    def test_team_init(self, mock_update, mock_api):
        # In practice, we'll pass an actual instance of Keybase. But for now,
        # We just need to be sure that the passed variables go to the right
        # places.
        mock_api.return_value = "api_instance"
        team = Team("test_team", "keybase_instance")
        mock_update.assert_called()
        mock_api.assert_called()
        self.assertEqual(team._api, "api_instance")
        self.assertEqual(team.name, "test_team")
        self.assertEqual(team._keybase, "keybase_instance")
        self.assertEqual(team.role, "None")

    @mock.patch("pykblib.team.KeybaseAPI.call_api")
    def test_team_update(self, mock_call_api):
        # First let's test a failure.
        mock_call_api.side_effect = APIException("Team doesn't exist.")
        with self.assertRaises(APIException):
            team = Team("test_team", "keybase_instance")
        mock_call_api.assert_called_with(
            "team",
            {
                "method": "list-team-memberships",
                "params": {"options": {"team": "test_team"}},
            },
        )
        mock_call_api.side_effect = None

        # Next, let's test a proper update.
        mock_call_api.return_value = dict_to_ntuple(
            {
                "result": {
                    "members": {
                        "owners": [{"username": "team_owner", "status": 0}],
                        "admins": [{"username": "team_admin", "status": 0}],
                        "writers": None,
                        "readers": [
                            {"username": "reader_1", "status": 0},
                            {"username": "reader_2", "status": 1},  # Reset.
                            {"username": "reader_3", "status": 2},  # Deleted.
                        ],
                    }
                }
            }
        )
        keybase = mock.MagicMock()
        keybase.username = "team_owner"
        team = Team("test_team", keybase)
        self.assertEqual(team.members_by_role.owner, {"team_owner"})
        self.assertEqual(team.members_by_role.admin, {"team_admin"})
        self.assertEqual(team.members_by_role.writer, set())
        self.assertEqual(team.members_by_role.reader, {"reader_1"})
        self.assertEqual(team.members_by_role.reset, {"reader_2"})
        self.assertEqual(team.members_by_role.deleted, {"reader_3"})
        self.assertEqual(team.role, "owner")

        # Finally, let's mix it up, to ensure the coder isn't being lazy.
        mock_call_api.return_value = dict_to_ntuple(
            {
                "result": {
                    "members": {
                        "owners": [{"username": "team_owner2", "status": 0}],
                        "admins": [],
                        "writers": [{"username": "team_writer2", "status": 0}],
                        "readers": [
                            {"username": "reader_1a", "status": 0},
                            {"username": "reader_2a", "status": 1},  # Reset.
                            {"username": "reader_3a", "status": 2},  # Deleted.
                        ],
                    }
                }
            }
        )
        keybase.username = "team_writer2"
        team = Team("test_team", keybase)
        self.assertEqual(team.members_by_role.owner, {"team_owner2"})
        self.assertEqual(team.members_by_role.admin, set())
        self.assertEqual(team.members_by_role.writer, {"team_writer2"})
        self.assertEqual(team.members_by_role.reader, {"reader_1a"})
        self.assertEqual(team.members_by_role.reset, {"reader_2a"})
        self.assertEqual(team.members_by_role.deleted, {"reader_3a"})
        self.assertEqual(team.role, "writer")


class TeamTest(TestCase):
    @mock.patch("pykblib.team.Team.update")
    @mock.patch("pykblib.team.KeybaseAPI", autospec=True)
    def setUp(self, mock_api, mock_update):
        keybase = mock.MagicMock()
        keybase.username = "test_user"
        self.team = Team("test_team", keybase)
        self.team._api = mock_api
        self.team.role = "owner"
        self.team.update = mock_update
        self.team.members_by_role = dict_to_ntuple(
            {
                "owner": {"test_user"},
                "admin": {"test_admin"},
                "writer": {"test_writer"},
                "reader": {"test_reader"},
                "reset": {"reset_user"},
                "deleted": {"deleted_user"},
            }
        )

    @mock.patch("pykblib.team.Team.add_members")
    def test_team_add_member(self, mock_add_members):
        username = random_username()
        role = random_role()
        self.team.add_member(username, role)
        mock_add_members.assert_called_with([username], role)
        self.team.add_member(username)
        mock_add_members.assert_called_with([username], "reader")

    def test_team_add_members(self):
        # Construct our first query.
        usernames = ["abraham", "barnabas", "charlize"]
        username_dict = [
            {"username": username, "role": "reader"} for username in usernames
        ]
        query = {
            "method": "add-members",
            "params": {
                "options": {"team": self.team.name, "usernames": username_dict}
            },
        }

        # Test failure.
        self.team._api.call_api.side_effect = APIException("EXCEPTION")
        with self.assertRaises(TeamException):
            self.team.add_members(usernames)
        self.team._api.call_api.assert_called_with("team", query)
        self.team._api.call_api.side_effect = None

        # Test success.
        # Generate a list of 3 to 7 random usernames.
        usernames = [random_username() for _ in range(random.randint(3, 7))]
        # Select a random role to add them to.
        role = random_role()
        # Change the team name.
        self.team.name = "bozo_bongo"
        # Update the query.
        username_dict = [
            {"username": username, "role": role} for username in usernames
        ]
        query = {
            "method": "add-members",
            "params": {
                "options": {"team": self.team.name, "usernames": username_dict}
            },
        }
        # Ensure they are successfully added.
        self.team._api.call_api.return_vaue = "Success"
        self.team.add_members(usernames, role)
        roles = self.team.members_by_role._asdict()
        self.assertFalse(any([name not in roles[role] for name in usernames]))
        self.team._api.call_api.assert_called_with("team", query)

    def test_team_change_member_role(self):
        # Create a random user and add them to a random role.
        old_role = random_role()
        new_role = random_role()
        while new_role == old_role:
            new_role = random_role()
        username = random_username()
        member_dict = self.team.members_by_role._asdict()
        member_dict[old_role].add(username)
        self.team.members_by_role = dict_to_ntuple(member_dict)
        self.team.name = random_username()
        query = {
            "method": "edit-member",
            "params": {
                "options": {
                    "team": self.team.name,
                    "username": username,
                    "role": new_role,
                }
            },
        }
        self.team.change_member_role(username, new_role)
        self.team._api.call_api.assert_called_with("team", query)
        member_dict = self.team.members_by_role._asdict()
        self.assertIn(username, member_dict[new_role])
        self.assertNotIn(username, member_dict[old_role])
        self.team._api.call_api.side_effect = APIException("EXCEPTION")
        with self.assertRaises(TeamException):
            self.team.change_member_role(username, new_role)

    def test_team_create_sub_team(self):
        # First, let's test a couple failures.
        self.team._keybase.create_team.side_effect = KeybaseException(
            "Could not create team test_team.sub_team."
        )
        with self.assertRaises(TeamException):
            self.team.create_sub_team("sub_team")
        self.team._keybase.create_team.assert_called_with("test_team.sub_team")

        # Now, let's test a success.
        self.team._keybase.create_team.side_effect = None
        self.team._keybase.create_team.return_value = "team_instance"
        self.assertEqual(
            self.team.create_sub_team("sub_team2"), "team_instance"
        )

        # And another, so our coder can't be lazy.
        self.team._keybase.create_team.return_value = "different_string"
        self.assertEqual(
            self.team.create_sub_team("sub_team2"), "different_string"
        )

    def test_team_delete(self):
        self.team.delete()
        self.team._keybase.delete_team.assert_called_with(self.team.name)
        self.team.name = "fake_name"
        self.team.delete()
        self.team._keybase.delete_team.assert_called_with("fake_name")

    def test_ignore_request(self):
        username = random_username()
        self.team.ignore_request(username)
        self.team._keybase.ignore_request.assert_called_with(
            self.team.name, username
        )
        self.team.name = random_username()
        self.team.ignore_request(username)
        self.team._keybase.ignore_request.assert_called_with(
            self.team.name, username
        )

    def test_team_leave(self):
        self.team.leave()
        self.team._keybase.leave_team.assert_called_with(self.team.name)
        random_name = random_username()
        self.team.name = random_name
        self.team.leave()
        self.team._keybase.leave_team.assert_called_with(random_name)

    def test_team_list_requests(self):
        set_of_users = {random_username() for _ in range(3)}
        random_return_value = {self.team.name: set_of_users}
        self.team._keybase.list_requests.return_value = random_return_value
        response = self.team.list_requests()
        self.assertEqual(response, set_of_users)
        self.team._keybase.list_requests.assert_called_with(self.team.name)
        self.team.name = random_username()
        random_return_value = {self.team.name: set_of_users}
        self.team._keybase.list_requests.return_value = random_return_value
        self.team.list_requests()
        self.team._keybase.list_requests.assert_called_with(self.team.name)

    def test_team_members(self):
        members = self.team.members()
        self.assertEqual(
            members,
            {
                "test_user",
                "test_admin",
                "test_writer",
                "test_reader",
                "reset_user",
                "deleted_user",
            },
        )
        self.team.members_by_role.owner.add("fake_user")
        members = self.team.members()
        self.assertEqual(
            members,
            {
                "test_user",
                "test_admin",
                "test_writer",
                "test_reader",
                "reset_user",
                "deleted_user",
                "fake_user",
            },
        )

    @mock.patch("pykblib.team.Team.remove_member")
    def test_team_purge_deleted(self, mock_remove_member):
        # Ensure it's removing our reset user.
        self.team.purge_deleted()
        mock_remove_member.assert_called_with("deleted_user")

        # Try with a random username.
        member_dict = self.team.members_by_role._asdict()
        username = random_username()
        member_dict["deleted"] = {username}
        self.team.members_by_role = dict_to_ntuple(member_dict)
        # This time we'll make it fail.
        mock_remove_member.side_effect = TeamException("EXCEPTION")
        with self.assertRaises(TeamException):
            self.team.purge_deleted()
        mock_remove_member.assert_called_with(username)

    @mock.patch("pykblib.team.Team.remove_member")
    def test_team_purge_reset(self, mock_remove_member):
        # Ensure it's removing our reset user.
        self.team.purge_reset()
        mock_remove_member.assert_called_with("reset_user")

        # Try with a random username.
        member_dict = self.team.members_by_role._asdict()
        username = random_username()
        member_dict["reset"] = {username}
        self.team.members_by_role = dict_to_ntuple(member_dict)
        # This time we'll make it fail.
        mock_remove_member.side_effect = TeamException("EXCEPTION")
        with self.assertRaises(TeamException):
            self.team.purge_reset()
        mock_remove_member.assert_called_with(username)

    def test_team_remove_member(self):
        # Test a failure first.
        self.team._api.call_api.side_effect = APIException("ANY ERROR")
        with self.assertRaises(TeamException):
            self.team.remove_member("test_writer")
        self.team._api.call_api.assert_called_with(
            "team",
            {
                "method": "remove-member",
                "params": {
                    "options": {
                        "team": self.team.name,
                        "username": "test_writer",
                    }
                },
            },
        )
        self.team._api.call_api.side_effect = None

        # Test a success next.
        self.team.name = "crazy_bunch"
        # Add a random user to the team.
        username = random_username()
        role = random_role()
        member_dict = self.team.members_by_role._asdict()
        member_dict[role].add(username)
        # Remove that user from the team.
        self.team.remove_member(username)
        self.team._api.call_api.assert_called_with(
            "team",
            {
                "method": "remove-member",
                "params": {
                    "options": {"team": self.team.name, "username": username}
                },
            },
        )
        self.assertNotIn(username, member_dict[role])

    def test_team_rename(self):
        # First, let's test failure.
        self.team._api.call_api.side_effect = APIException("EXCEPTION")
        self.team.name = "test_team.subteam"
        with self.assertRaises(TeamException):
            self.team.rename("new_name")
        self.team._api.call_api.assert_called_with(
            "team",
            {
                "method": "rename-subteam",
                "params": {
                    "options": {
                        "team": "test_team.subteam",
                        "new-team-name": "test_team.new_name",
                    }
                },
            },
        )
        self.team._api.call_api.side_effect = None

        # Next, let's test success.
        self.team._api.call_api.return_value = dict_to_ntuple(
            {"result": "success"}
        )
        self.team.rename("new_name2")
        self.team._keybase._update_team_name.assert_called_with(
            "test_team.subteam", "test_team.new_name2"
        )

    def test_team_sub_team(self):
        team_instance = mock.MagicMock()
        self.team._keybase.team.return_value = team_instance
        sub_team = self.team.sub_team("subteam")
        self.team._keybase.team.assert_called_with("test_team.subteam")
        self.team.name = "different_name"
        sub_team = self.team.sub_team("subteam2")
        self.team._keybase.team.assert_called_with("different_name.subteam2")
        self.assertEqual(sub_team, team_instance)

    def test_team_update_parent_team_name(self):
        self.team.name = "test_team.subteam"
        self.team._update_parent_team_name("test_team", "new_team")
        self.assertEqual(self.team.name, "new_team.subteam")
        self.team._update_parent_team_name("new_team", "newer_team")
        self.assertEqual(self.team.name, "newer_team.subteam")
