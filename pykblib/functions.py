"""Defines various PyKBLib internal functions."""

import json
import pipes
import time

import pexpect
from steffentools import dict_to_ntuple


def _api_base(service, query, attempts=0):
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
    if attempts > 3:
        # Try up to three times before returning False if we have a signature
        # error. This crops up occasionally.
        return False
    query = json.dumps(query)
    response = _run_command(["keybase", service, "api", "-m", query])
    response = json.loads(response)
    if hasattr(response, "error"):
        if "bad signature" in response.error.message:
            # This seems to be caused by lag between the client and server in
            # the Keybase implementation, and the only solution I know of is
            # to wait for it to pass.
            time.sleep(5)
            return _api_base(service, query, attempts + 1)
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


def _delete_team(team_name):
    """Attempt to delete the specified team.

    Parameters
    ----------
    team_name : str
        The name of the team to be deleted.

    Returns
    -------
    bool
        `True` or `False`, dependent on whether the function succeeded.

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
        return False
    proc.sendline("nuke {}\r\n".format(team_name))
    output = bytes()
    # Read output until EOF.
    while 1:
        try:
            output += proc.read_nonblocking(timeout=3)
        except (pexpect.exceptions.TIMEOUT, pexpect.exceptions.EOF):
            break
    return "Success!" in output.decode()


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


def _run_command(command_list, attempts=0):
    """Execute a console command and retrieve the result.

    This function is only intended to be used with Keybase console commands. It
    will make three attempts to run the specified command. Each time it fails,
    it will attempt to restart the keybase daemon before making another
    attempt. After the third failed attempt, it will raise the TimeoutExpired
    error. Any other error encountered will be raised regardless.

    Parameters
    ----------
    command_list : list
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
    if attempts > 3:
        return False
    try:
        command = " ".join(pipes.quote(arg) for arg in command_list)
        return pexpect.run(command).decode()
    except pexpect.exceptions.TIMEOUT:
        pexpect.run("keybase ctl restart")
        return _run_command(command_list, attempts + 1)
