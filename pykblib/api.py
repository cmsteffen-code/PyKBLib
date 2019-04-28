"""Defines the KeybaseAPI class."""

import json
import shlex

import pexpect
from steffentools import dict_to_ntuple

from pykblib.exceptions import APIException


class KeybaseAPI:
    """Provides an interface to the Keybase service."""

    def call_api(self, service, query):
        """Execute the specified query on the specified API service.

        Parameters
        ----------
        service : str
            The name of the API service, i.e. 'chat', 'team', or 'wallet'.
        query : dict
            The query to be sent to the API.

        Returns
        -------
        result : namedtuple
            The result of the query, converted into a nested namedtuple.

        Raises
        ------
        APIException
            If there is an error defined in the return value, this will raise
            an exception containing the error message.

        """
        json_query = json.dumps(query)
        command = "{} api -m {}".format(service, shlex.quote(json_query))
        json_result = self.run_command(command)
        result = json.loads(json_result)
        if "error" in result.keys():
            raise APIException(result["error"]["message"])
        return dict_to_ntuple(result)

    @staticmethod
    def delete_team(team_name):
        """Delete the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team to be deleted.

        Raises
        ------
        APIException
            If the team cannot be deleted, the APIException will be raised.

        """
        # This is a special function. Where most actions are able to be
        # executed via the _run_command function, keybase team deletion is a
        # bit more complicated.

        # Open a new pexpect process for deletion.
        proc = pexpect.spawn("keybase team delete {}".format(team_name))
        try:
            proc.expect("WARNING", timeout=10)
        except (pexpect.exceptions.TIMEOUT, pexpect.exceptions.EOF):
            # If it didn't give us a warning, then we can't delete this team.
            raise APIException("Failed to delete team {}.".format(team_name))
        proc.sendline("nuke {}\r\n".format(team_name))
        output = bytes()
        # Read output until EOF.
        while 1:
            try:
                output += proc.read_nonblocking(timeout=3)
            except (pexpect.exceptions.TIMEOUT, pexpect.exceptions.EOF):
                break
        if "Success!" not in output.decode():
            raise APIException("Failed to delete team {}.".format(team_name))

    @staticmethod
    def run_command(command):
        """Execute the specified command, then return the result.

        Parameters
        ----------
        command : str
            The command to be run.

        Returns
        -------
        output : str
            The output of the command being run.

        Raises
        ------
        APIException
            If there was an error returned by the Keybase application, this
            will raise an exception containing the error message.

        """
        result = pexpect.run("keybase {}".format(command))
        if b"\x1b[31m" in result and b"ERROR" in result:
            # An error was reported. Exctract the message and raise it.
            result = b" ".join(result.split()[2:]).replace(b"\x1b[0m", b"")
            raise APIException(result.decode())
        return result.decode()
