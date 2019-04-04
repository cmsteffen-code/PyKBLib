"""PyKBLib Utility Functions."""

import json
import subprocess

from steffentools import dict_to_ntuple


def _api_base(service, query):
    """Send a query to the specified service API.

    Parameters
    ----------
    query : dict
        The API query in dict format.
    service : str
        The API service to which the query will be sent, such as 'chat', 'team'
        or 'wallet'.

    Returns
    -------
    result : namedtuple
        The API result in namedtuple format.

    """
    query = json.dumps(query)
    response = _run_command(["keybase", service, "api", "-m", query])
    response = json.loads(response)
    return dict_to_ntuple(response)


def _api_chat(query):
    """Send a query to the Chat API.

    Parameters
    ----------
    query : dict
        The API query in dict format.

    Returns
    -------
    result : namedtuple
        The API result in namedtuple format.

    """
    return _api_base("chat", query)


def _api_team(query):
    """Send a query to the Team API.

    Parameters
    ----------
    query : dict
        The API query in dict format.

    Returns
    -------
    result : namedtuple
        The API result in namedtuple format.

    """
    return _api_base("team", query)


def _api_wallet(query):
    """Send a query to the Wallet API.

    Parameters
    ----------
    query : dict
        The API query in dict format.

    Returns
    -------
    result : namedtuple
        The API result in namedtuple format.

    """
    return _api_base("wallet", query)


def _get_memberships(username):
    """Get a list of the teams to which the specified user belongs.

    Parameters
    ----------
    username : str
        The target user.

    Returns
    -------
    team_list : list
        A list of all the teams of which the active user is a member.

    """
    # Get the list of team memberships.
    response = _api_team(
        {
            "method": "list-user-memberships",
            "params": {"options": {"username": username}},
        }
    )
    # Extract the team names from the response.
    team_list = list()
    if response.result.teams is not None:
        for team in response.result.teams:
            team_list.append(team.fq_name)
    return team_list


def _get_username():
    """Get the name of the user currently logged in.

    Returns
    -------
    username : str
        The username of the currently active Keybase user.

    """
    # Run the command and retrieve the result.
    result = _run_command(["keybase", "status"])
    # Extract the username from the result.
    username = result.split("\n")[0].split(":")[-1].strip()
    # Return the username.
    return username


def _run_command(command):
    """Execute a console command and retrieve the result.

    This function is only intended to be used with Keybase console commands. It
    will make three attempts to run the specified command. Each time it fails,
    it will attempt to restart the keybase daemon before making another
    attempt. After the third failed attempt, it will raise the TimeoutExpired
    error. Any other error encountered will be raised regardless.

    Parameters
    ----------
    command : list
        The command to be executed. This command is in the form of a list, with
        the command and each argument in its own element. For example:

            keybase team add-member pykblib_dev -u pykblib -r reader -s

        would become:

            [
                "keybase",
                "team",
                "add-member",
                "pykblib_dev",
                "-u",
                "pykblib",
                "-r",
                "reader",
                "-s",
            ]

    Returns
    -------
    str
        The command-line output.

    """
    attempts = 0
    while True:
        try:
            # Attempt to execute the specified command and retrieve the result.
            return subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                shell=False,
                timeout=10,  # Raise an exception if this takes > 10 seconds.
            ).decode()
        except subprocess.TimeoutExpired:
            # When the call times out, check how many times it has failed.
            if attempts > 3:
                # If it's failed more than three times, raise the exception.
                raise
            # If it hasn't failed three times yet, restart they keybase daemon.
            subprocess.check_output("keybase ctl restart", shell=True)
            # Increment the number of attempts.
            attempts += 1
