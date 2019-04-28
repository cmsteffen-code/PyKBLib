"""Test the PyKBLib Keybase class."""

from unittest import TestCase, mock

from steffentools import dict_to_ntuple

from pykblib.exceptions import APIException, KeybaseException, TeamException
from pykblib.keybase import Keybase


class KeybaseInitializationTest(TestCase):
    @mock.patch("pykblib.keybase.Keybase.update_team_list")
    @mock.patch("pykblib.keybase.Keybase._get_username")
    def test_keybase_init(self, mock_get_username, mock_update_team_list):
        mock_get_username.return_value = "testuser"
        keybase = Keybase()
        mock_get_username.assert_called()
        mock_update_team_list.assert_called()

    @mock.patch("pykblib.keybase.KeybaseAPI.run_command")
    @mock.patch("pykblib.keybase.Keybase.update_team_list")
    def test_keybase_get_username(
        self, mock_update_team_list, mock_run_command
    ):
        mock_run_command.return_value = "\n".join(
            ["Username:      testuser", "Logged in:     yes"]
        )
        keybase = Keybase()
        self.assertEqual(keybase.username, "testuser")
        mock_run_command.assert_called_with("status")
        mock_run_command.return_value = "\n".join(
            ["Username:      testuser", "Logged in:     no"]
        )
        with self.assertRaises(KeybaseException):
            keybase._get_username()

    @mock.patch("pykblib.keybase.KeybaseAPI.call_api")
    @mock.patch("pykblib.keybase.Keybase._get_username")
    def test_keybase_update_team_list(self, mock_get_username, mock_call_api):
        mock_get_username.return_value = "testuser"
        # Simulate a real API return value.
        mock_call_api.return_value = dict_to_ntuple(
            {
                "result": {
                    "teams": [
                        {
                            "uid": "fake_uid",
                            "team_id": "fake_team_id",
                            "username": "testuser",
                            "full_name": "Test User",
                            "fq_name": "example_team",
                            "is_implicit_team": False,
                            "implicit_team_display_name": "",
                            "is_open_team": False,
                            "role": 4,
                            "needsPUK": False,
                            "member_count": 7,
                            "member_eldest_seqno": 0,
                            "allow_profile_promote": False,
                            "is_member_showcased": False,
                            "status": 0,
                        }
                    ],
                    "annotatedActiveInvites": {},
                }
            }
        )
        keybase = Keybase()
        mock_call_api.assert_called_with(
            "team",
            {
                "method": "list-user-memberships",
                "params": {"options": {"username": "testuser"}},
            },
        )
        self.assertEqual(keybase.teams, ["example_team"])
        keybase.update_team_list()
        self.assertEqual(keybase.teams, ["example_team"])


class KeybaseTest(TestCase):
    @mock.patch("pykblib.keybase.Keybase.update_team_list")
    @mock.patch("pykblib.keybase.Keybase._get_username")
    @mock.patch("pykblib.keybase.KeybaseAPI", autospec=True)
    def setUp(self, mock_api, mock_get_username, mock_update_team_list):
        mock_get_username.return_value = "testuser"
        self.keybase = Keybase()
        self.keybase._api = mock_api
        self.keybase.teams = ["team_one", "team_one.subteam", "second_team"]
        self.keybase._get_username = mock_get_username
        self.keybase.update_team_list = mock_update_team_list

    @mock.patch("pykblib.keybase.Keybase.team")
    def test_keybase_create_team(self, mock_team):
        # First let's test a failed attempt.
        self.keybase._api.call_api.side_effect = APIException("EXCEPTION")
        with self.assertRaises(KeybaseException):
            self.keybase.create_team("team_two")
        self.keybase._api.call_api.assert_called_with(
            "team",
            {
                "method": "create-team",
                "params": {"options": {"team": "team_two"}},
            },
        )
        self.keybase._api.call_api.side_effect = None

        # Next, let's try a different failed attempt.
        self.keybase._api.call_api.return_value = dict_to_ntuple(
            {"result": {"chatSent": False}}
        )
        with self.assertRaises(KeybaseException):
            new_team = self.keybase.create_team("team_one")

        # Next, let's try a successful response.
        self.keybase._api.call_api.return_value = dict_to_ntuple(
            {"result": {"chatSent": True, "creatorAdded": True}}
        )
        new_team = self.keybase.create_team("team_two")
        self.assertTrue("team_two" in self.keybase.teams)
        mock_team.assert_called_with("team_two")

        # Finally, let's try a different successful response. When making a
        # sub-team, the "creatorAdded" value will be False.
        self.keybase._api.call_api.return_value = dict_to_ntuple(
            {"result": {"chatSent": True, "creatorAdded": False}}
        )
        new_team = self.keybase.create_team("team_three")
        self.assertTrue("team_three" in self.keybase.teams)
        mock_team.assert_called_with("team_three")

    def test_keybase_delete_team(self):
        # First, let's test a failure. In this case, the team isn't in the
        # teams list.
        with self.assertRaises(KeybaseException):
            self.keybase.delete_team("team_one.subteam2")

        # Next, let's test an APIException failure.
        self.keybase._api.delete_team.side_effect = APIException(
            "Could not delete team."
        )
        with self.assertRaises(KeybaseException):
            self.keybase.delete_team("team_one")
        self.keybase._api.delete_team.side_effect = None

        # Next, let's test a success.
        self.keybase._active_teams["second_team"] = "placeholder"
        self.keybase.delete_team("second_team")
        self.assertFalse("second_team" in self.keybase.teams)
        self.assertFalse("second_team" in self.keybase._active_teams.keys())
        self.keybase._api.delete_team.assert_called_with("second_team")

        # Finally, let's ensure that subteams are deleted before root teams.
        self.keybase._api.delete_team.side_effect = [
            None,
            APIException("Failed to delete team team_one."),
        ]
        with self.assertRaises(KeybaseException):
            self.keybase.delete_team("team_one")
        # If the sub-team was deleted first, it should not be in keybase.teams,
        # but the root team should still be there since we raised an error on
        # the second api.delete_team call.
        self.assertTrue("team_one" in self.keybase.teams)
        self.assertTrue("team_one.subteam" not in self.keybase.teams)

    def test_keybase_ignore_request(self):
        # First let's test a failed attempt.
        self.keybase._api.run_command.side_effect = APIException("EXCEPTION")
        with self.assertRaises(KeybaseException):
            self.keybase.ignore_request("test_team", "fake_username")
        self.keybase._api.run_command.assert_called_with(
            "team ignore-request test_team -u fake_username"
        )

        # Now let's try successful attempts.
        self.keybase._api.run_command.side_effect = APIException("Not found")
        self.keybase.ignore_request("test_team", "fake_username")
        self.keybase._api.run_command.side_effect = None
        self.keybase._api.run_command.return_value = "Success!"
        self.keybase.ignore_request("test_team", "fake_username")

    def test_keybase_leave_team(self):
        # First let's test a failed attempt.
        self.keybase._api.call_api.side_effect = APIException("EXCEPTION")
        with self.assertRaises(KeybaseException):
            self.keybase.leave_team("team_one")
        self.keybase._api.call_api.assert_called_with(
            "team",
            {
                "method": "leave-team",
                "params": {
                    "options": {"team": "team_one", "permanent": False}
                },
            },
        )

        # Next, let's try some successful responses.
        self.keybase.teams.append("team_two")
        self.keybase._active_teams["team_two"] = "placeholder"
        self.keybase._api.call_api.side_effect = APIException(
            "not a member of team"
        )
        # Despite the exception thrown above, this should not raise an error.
        self.keybase.leave_team("team_two")
        self.assertTrue("team_two" not in self.keybase.teams)
        self.assertTrue("team_two" not in self.keybase._active_teams.keys())
        self.keybase._api.call_api.side_effect = None
        self.keybase._api.call_api.return_value = dict_to_ntuple(
            {"response": "success"}
        )
        self.keybase.leave_team("team_one")
        self.assertTrue("team_one" not in self.keybase.teams)

    def test_keybase_list_requests(self):
        # First, let's test a failed attempt.
        self.keybase._api.run_command.return_value = "ERROR"
        with self.assertRaises(KeybaseException):
            self.keybase.list_requests()
        self.keybase._api.run_command.assert_called_with("team list-requests")

        # Next, let's test an empty list.
        self.keybase._api.run_command.return_value = "No requests at this time"
        result = self.keybase.list_requests()
        self.assertEqual(result, dict())

        # Next, let's test a request for all teams.
        self.keybase._api.run_command.return_value = "\n".join(
            [
                "team_one          test_user wants to join",
                "team_one          test_user2 wants to join",
                "team_one.subteam  test_user wants to join",
                (
                    "-----------------------------------"
                    "-----------------------------------"
                ),
                (
                    "To handle requests, use `keybase team add-member` "
                    "or `keybase team ignore-request`."
                ),
            ]
        )
        result = self.keybase.list_requests()
        self.assertEqual(
            result,
            {
                "team_one": {"test_user", "test_user2"},
                "team_one.subteam": {"test_user"},
            },
        )

        # Finally, let's test a request for a single team.
        self.keybase._api.run_command.return_value = "\n".join(
            [
                "team_one.subteam  test_user wants to join",
                (
                    "-----------------------------------"
                    "-----------------------------------"
                ),
                (
                    "To handle requests, use `keybase team add-member` "
                    "or `keybase team ignore-request`."
                ),
            ]
        )
        result = self.keybase.list_requests("team_one.subteam")
        self.keybase._api.run_command.assert_called_with(
            "team list-requests -t team_one.subteam"
        )
        self.assertEqual(result, {"team_one.subteam": {"test_user"}})

    def test_keybase_request_access(self):
        # First let's test a failed attempt.
        self.keybase._api.run_command.return_value = "error message"
        with self.assertRaises(KeybaseException):
            self.keybase.request_access("test_team")
        self.keybase._api.run_command.assert_called_with(
            "team request-access test_team"
        )

        # Now let's test a success.
        self.keybase._api.run_command.return_value = "an email has been sent"
        self.keybase.request_access("test_team")
        self.keybase._api.run_command.return_value = "You have joined"
        self.keybase.request_access("test_team")
        self.keybase._api.run_command.side_effect = APIException(
            "access already requested"
        )
        self.keybase.request_access("test_team")

    @mock.patch("pykblib.keybase.Team")
    def test_keybase_team(self, mock_team):
        # Let's test failure.
        mock_team.side_effect = TeamException("Some words.")
        with self.assertRaises(KeybaseException):
            self.keybase.team("team_name")
        mock_team.assert_called_with("team_name", self.keybase)

        # Let's test success.
        mock_team.side_effect = None
        team = mock.MagicMock()
        team.name = "team_name2"
        mock_team.return_value = team
        new_team = self.keybase.team("team_name2")
        mock_team.assert_called_with("team_name2", self.keybase)
        self.assertEqual(new_team, team)
        self.assertEqual(self.keybase._active_teams["team_name2"], team)

    def test_keybase_update_team_name(self):
        test_team = mock.MagicMock()
        self.keybase._active_teams["team_one"] = test_team
        test_sub_team = mock.MagicMock()
        self.keybase._active_teams["team_one.subteam"] = test_sub_team

        # Change the team name.
        self.keybase._update_team_name("team_one", "team_1")
        test_sub_team._update_parent_team_name.assert_called_with(
            "team_one", "team_1"
        )
        self.assertNotIn("team_one", self.keybase._active_teams.keys())
        self.assertNotIn("team_one.subteam", self.keybase._active_teams.keys())
        self.assertEqual(self.keybase._active_teams["team_1"], test_team)
        self.assertEqual(
            self.keybase._active_teams["team_1.subteam"], test_sub_team
        )
        self.assertNotIn("team_one", self.keybase.teams)
        self.assertNotIn("team_one.subteam", self.keybase.teams)
        self.assertIn("team_1", self.keybase.teams)
        self.assertIn("team_1.subteam", self.keybase.teams)

        # Change it back.
        self.keybase._update_team_name("team_1", "team_one")
        test_sub_team._update_parent_team_name.assert_called_with(
            "team_1", "team_one"
        )
        self.assertNotIn("team_1", self.keybase._active_teams.keys())
        self.assertNotIn("team_1.subteam", self.keybase._active_teams.keys())
        self.assertEqual(self.keybase._active_teams["team_one"], test_team)
        self.assertEqual(
            self.keybase._active_teams["team_one.subteam"], test_sub_team
        )
        self.assertNotIn("team_1", self.keybase.teams)
        self.assertNotIn("team_1.subteam", self.keybase.teams)
        self.assertIn("team_one", self.keybase.teams)
        self.assertIn("team_one.subteam", self.keybase.teams)

        # Update a team that doesn't exist.
        self.keybase._update_team_name("not_a_team", "fake_name")
