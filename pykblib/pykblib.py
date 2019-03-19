"""Contains the core functionality of the pykblib library."""


import subprocess

from steffentools import dict_to_ntuple


class Keybase:
    """The primary point of interaction with PyKBLib.

    Attributes
    ----------
    teams : list
        A list of the names of teams to which the active user is subscribed.
    username : str
        The name of the user logged into Keybase.

    """

    # Private Attributes
    # ------------------
    # _team_data : dict
    #     A dictionary of the teams to which the user belongs, corresponding
    #     with their roles and the number of users in each team.

    def __init__(self):
        """Initialize the Keybase class."""
        self.update_team_list()
        self.username = _get_username()

    def team(self, team_name: str):
        """Return a Team class instance for the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team to which the Team class should refer.

        Returns
        -------
        team_instance : Team
            The Team class instance created by the function.

        """
        # Create the new Team instance.
        team_instance = Team(team_name)
        # Set the member_count attribute of the team.
        team_instance._set_member_count(self._team_data[team_name].member_count)
        # Set the roles attribute of the team.
        team_instance._set_roles(self._team_data[team_name].roles)
        # Return the new team instance.
        return team_instance

    def update_team_list(self):
        """Update the Keybase.teams attribute."""
        # Retrieve information about the team memberships.
        self._team_data = _get_memberships()
        # Extract the list of team names and store it in the teams attribute.
        self.teams = list(self._team_data.keys())


class Team:
    """An instance of a Keybase team.

    Attributes
    ----------
    member_count : int
        The number of members in the team, as of the object creation time.
    name : str
        The name of the team.
    roles : list
        A list of the roles assigned to the active user within this team.

    """

    def __init__(self, name: str):
        """Initialize the Team class."""
        self.name = name

    def _set_member_count(self, count: int):
        """Set the member_count attribute for this team.

        Parameters
        ----------
        count : int
            The number of members in the team.

        """
        self.member_count = count

    def _set_roles(self, roles: list):
        """Set the roles attribute for this team.

        Parameters
        ----------
        roles : list
            The list of this team's roles to which the active user is assigned.

        """
        self.roles = roles


def _get_memberships():
    """Get a dictionary of the teams to which the user belongs.

    Returns
    -------
    team_dict : dict
        A dict comprising named tuples for each of the teams to which the user
        belongs, corresponding with their roles and the number of users in each
        team. The elements are accessed as follows:

        **team_dict[team_name].roles** : list
            The list of roles assigned to the user for this team.
        **team_dict[team_name].member_count** : int
            The number of members in this team.

    """
    # Run the command and retrieve the result.
    result = _run_command("keybase team list-memberships")
    # Parse the result into a list. We skip the first line because it simply
    # states the column names.
    team_list = [item for item in result.split("\n")[1:-1]]
    # Create the team_dict dictionary.
    team_dict = dict()
    # Parse the team list into the memberships dictionary.
    for team in team_list:
        [name, roles, member_count] = [
            item.strip() for item in team.split("    ") if item != ""
        ]
        # Extract the list of roles.
        roles = roles.split(", ")
        # Create a team_data dictionary with the roles and member count.
        team_data = {"roles": roles, "member_count": int(member_count)}
        # Convert the team_data to a namedtuple and assign it to the team_dict.
        team_dict[name] = dict_to_ntuple(team_data)
    # Return the team dictionary.
    return team_dict


def _get_username():
    """Get the name of the user currently logged in.

    Returns
    -------
    username : str
        The username of the currently active Keybase user.

    """
    # Run the command and retrieve the result.
    result = _run_command("keybase status")
    # Extract the username from the result.
    username = result.split("\n")[0].split(":")[-1].strip()
    # Return the username.
    return username


def _run_command(command_string: str):
    """Execute a console command and retrieve the result.

    This function is only intended to be used with Keybase console commands. It
    will make three attempts to run the specified command. Each time it fails,
    it will attempt to restart the keybase daemon before making another
    attempt.

    Parameters
    ----------
    command_string : str
        The command to be executed.

    """
    attempts = 0
    while True:
        try:
            # Attempt to execute the specified command and retrieve the result.
            return subprocess.check_output(
                command_string,
                stderr=subprocess.STDOUT,
                shell=True,
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
