"""Test the PyKBLib Keybase API class."""

from unittest import TestCase, mock

import pexpect

from pykblib.api import KeybaseAPI
from pykblib.exceptions import APIException


class KeybaseAPITest(TestCase):
    def setUp(self):
        self.api = KeybaseAPI()

    @mock.patch("pykblib.api.dict_to_ntuple")
    @mock.patch("pykblib.api.KeybaseAPI.run_command")
    def test_api_call_api(self, mock_run_command, mock_dict_to_ntuple):
        demo_query = {"method": "demo"}
        # We want to ensure that the call_api raises an exception when it gets
        # an error from Keybase.
        mock_run_command.return_value = '{"error":{"message":"error message"}}'
        with self.assertRaises(APIException):
            self.api.call_api("team", demo_query)
        mock_run_command.assert_called_with(
            'team api -m \'{"method": "demo"}\''
        )
        # Now check a working query.
        mock_run_command.return_value = '{"result": "success"}'
        mock_dict_to_ntuple.return_value = "Success"
        self.assertEqual(self.api.call_api("team", demo_query), "Success")
        mock_dict_to_ntuple.assert_called_with({"result": "success"})

    @mock.patch("pykblib.api.pexpect.spawn")
    def test_api_delete_team(self, mock_spawn):
        mock_child = mock.MagicMock()
        mock_spawn.return_value = mock_child

        # First let's test failure at the spawn phase.
        mock_child.expect.side_effect = pexpect.exceptions.EOF("ERROR")
        with self.assertRaises(APIException):
            self.api.delete_team("test_team")
        mock_spawn.assert_called_with("keybase team delete test_team")
        mock_child.expect.assert_called_with("WARNING", timeout=10)

        # Next, let's test failure at the success phase.
        mock_child.expect.side_effect = None
        mock_child.read_nonblocking.side_effect = [
            b"Failure!",
            pexpect.exceptions.EOF("ERROR"),
        ]
        with self.assertRaises(APIException):
            self.api.delete_team("test_team")
        mock_child.sendline.assert_called_with("nuke test_team\r\n")
        mock_child.read_nonblocking.assert_called_with(timeout=3)

        # Next, let's test success. This should raise no exceptions.
        mock_child.read_nonblocking.side_effect = [
            b"Success!",
            pexpect.exceptions.EOF("EOF"),
        ]
        self.api.delete_team("test_team")

    @mock.patch("pykblib.api.pexpect.run")
    def test_api_run_command(self, mock_run):
        # The pexpect.run function returns a bytes object.
        mock_run.return_value = b"return value"
        # The KeybaseAPI.run_command function should convert bytes to string.
        self.assertEqual(self.api.run_command("test command"), "return value")
        mock_run.assert_called_with("keybase test command")
        # Test error capturing and exception raising.
        mock_run.return_value = (
            b"\x1b[31m\xe2\x96\xb6 ERROR Team "
            + b'"cancel" does not exist\x1b[0m\r\n'
        )
        with self.assertRaises(APIException):
            self.api.run_command("test command")
