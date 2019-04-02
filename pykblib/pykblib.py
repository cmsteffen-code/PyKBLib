"""Contains the core functionality of the pykblib library."""

import json
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
        self.username = _get_username()
        self.update_team_list()

    def create_team(self, team_name: str):
        """Attempt to create a new Keybase Team.

        If the team is successfully created, the team's name will be added to
        the `Keybase.teams` list and an instance of `Team` will be returned.
        Otherwise, the function will return `False`.

        Parameters
        ----------
        team_name : str
            The name of the team to be created.

        Returns
        -------
        Team or False
            If the team is successfully created, this function will return a
            Team object for the new team. Otherwise, it will return False.

        """
        query = {
            "method": "create-team",
            "params": {"options": {"team": team_name}},
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        self.teams.append(team_name)
        self.teams.sort()
        return self.team(team_name)

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
        team_instance = Team(team_name, self)
        # Return the new team instance.
        return team_instance

    def update_team_list(self):
        """Update the Keybase.teams attribute."""
        # Retrieve information about the team memberships.
        self._team_data = _get_memberships(self.username)
        # Extract the list of team names and store it in the teams attribute.
        self.teams = list(self._team_data.keys())

    def update_team_name(self, old_name: str, new_name: str):
        """Attempt to update the name of a team in the teams list.

        Parameters
        ----------
        old_name : str
            The original name of the team.
        new_name : str
            The new name of the team.

        Returns
        -------
        bool
            Returns `True` or `False`, dependent on whether the update was
            successful.

        """
        try:
            self.teams[self.teams.index(old_name)] = new_name
            return new_name in self.teams
        except ValueError:
            # The team name wasn't in the list.
            return False


class Team:
    """An instance of a Keybase team.

    Attributes
    ----------
    name : str
        The name of the team.
    user : Keybase
        The active user. This is the instance of the Keybase class that created
        this Team instance.
    role : str
        The role assigned to the active user within this team.
    member_count : int
        The number of members in the team, as of the object creation time.
    members : list
        A list of the usernames of all active members in the team.
    members_by_role : namedtuple
        A namedtuple comprising lists of members by specified role. To access
        the lists, use one of the following:

        * **Team.members_by_role.owner**
        * **Team.members_by_role.admin**
        * **Team.members_by_role.writer**
        * **Team.members_by_role.reader**

    deleted : list
        A list of the usernames of all members who have deleted their accounts.

    """

    def __init__(self, name: str, user: Keybase):
        """Initialize the Team class."""
        self.name = name
        self.user = user
        # Update the member lists.
        assert self.update()

    def add_member(self, username: str, role: str = "reader"):
        """Attempt to add the specified user to this team.

        Parameters
        ----------
        username : str
            The username of the user to add to the team.
        role : str
            The role to assign to the new member. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team. *(Defaults to reader.)*

        Returns
        -------
        bool
            A boolean value which indicates whether the user was successfully
            added to the team. It will return True if the user was added, or
            False if the attempt failed. Note: This can fail if the user is
            already a member of the team, as well as for other problems.

        """
        return self.add_members([username], role)

    def add_members(self, usernames: list, role: str = "reader"):
        """Attempt to add the specified users to this team.

        Parameters
        ----------
        usernames : str
            The usernames of the users to add to the team.
        role : str
            The role to assign to the new members. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team. *(Defaults to reader.)*

        Returns
        -------
        bool
            A boolean value which indicates whether the users were successfully
            added to the team. It will return True if the users were added, or
            False if the attempt failed. Note: This can fail if the users are
            already a member of the team, as well as for other problems.

        """
        username_list = [
            {"username": username, "role": role} for username in usernames
        ]
        query = {
            "method": "add-members",
            "params": {
                "options": {"team": self.name, "usernames": username_list}
            },
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        return True

    def change_member_role(self, username: str, role: str):
        """Change the specified user's role within this team.

        Parameters
        ----------
        username : str
            The username of the member whose role will be changed.
        role : str
            The role to assign to the member. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team.

        Returns
        -------
        bool
            A boolean value which indicates whether the user's role was
            successfully changed. It will return True if the role was changed,
            or False if the role was not changed.

        """
        query = {
            "method": "edit-member",
            "params": {
                "options": {
                    "team": self.name,
                    "username": username,
                    "role": role,
                }
            },
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        return True

    def create_sub_team(self, team_name: str):
        """Attempt to create a sub-team within this team.

        This function simply calls `Keybase.create_team` with the appropriate
        full team name, a concatenation of the parent team and sub-team names,
        separated by a period.

        Parameters
        ----------
        team_name : str
            The name of the sub-team to be created. The final team name will be
            `parent_team.team_name` where `parent_team` is this team's name.

        Returns
        -------
        Team or False
            This will either return a new Team object if the sub-team is
            successfully created, or `False` if creation fails.

        """
        full_name = self.name + "." + team_name
        return self.user.create_team(full_name)

    def purge_deleted(self):
        """Purge deleted members from this team.

        Returns
        -------
        failures : list
            A list of members that were unable to be deleted. If all members
            were deleted successfully, this list will be empty.

        """
        failures = list()
        for username in self.deleted:
            if not self.remove_member(username):
                failures.append(username)
        return failures

    def remove_member(self, username: str):
        """Attempt to remove the specified user from this team.

        Parameters
        ----------
        username : str
            The username of the user to remove from the team.

        Returns
        -------
        bool
            A boolean value which indicates whether the user was successfully
            removed from the team. It will return True if the user was removed,
            or False if the attempt failed. Note: This can fail if the user is
            not a member of the team, as well as for other problems.

        """
        query = {
            "method": "remove-member",
            "params": {"options": {"team": self.name, "username": username}},
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        return True

    def rename(self, new_name: str):
        """Attempt to rename this team.

        This will only work if this team is a sub-team.

        Parameters
        ----------
        new_name : str
            The sub-team's new name.

        Returns
        -------
        bool
            The function will return either `True` or `False`, dependent upon
            the success of the name-change attempt.

        """
        if "." not in self.name:
            # We cannot change the name of top-level teams.
            return False
        new_name = ".".join(self.name.split(".")[:-1]) + "." + new_name
        query = {
            "method": "rename-subteam",
            "params": {
                "options": {"team": self.name, "new-team-name": new_name}
            },
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        self.user.update_team_name(self.name, new_name)
        self.name = new_name
        return True

    def update(self):
        """Update the team's membership and role information.

        Returns
        -------
        bool
            A boolean value representing the success or failure of the update.

        """
        query = {
            "method": "list-team-memberships",
            "params": {"options": {"team": self.name}},
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        # Retrieve the names of all members in each role.
        members_by_role = dict()
        self.deleted = list()
        self.members = list()
        roles = {
            "owner": response.result.members.owners,
            "admin": response.result.members.admins,
            "writer": response.result.members.writers,
            "reader": response.result.members.readers,
        }
        for role, member_list in roles.items():
            try:
                members_by_role[role] = list()
                for member in member_list:
                    if member.username == self.user.username:
                        # This is our entry, save our role.
                        self.role = role
                    if member.status == 2:
                        # This member has deleted their account.
                        self.deleted.append(member.username)
                    elif member.status == 0:
                        # This member is active.
                        self.members.append(member.username)
                        members_by_role[role].append(member.username)
                    else:
                        # This member is of an unknown status.
                        # TODO: Figure out the other possible statuses and add
                        # them to the script in order to finish this section.
                        print(
                            "Unknown member status for {}: {}".format(
                                member.username, member.status
                            )
                        )
                        self.members.append(member.username)
                        members_by_role[role].append(member.username)
            except TypeError:
                # We've already initialized the list for this role, so we don't
                # need to worry about handling this exception.
                pass
        self.member_count = len(self.members)
        self.members_by_role = dict_to_ntuple(members_by_role)
        return True


def _api_base(service: str, query: dict):
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
    response = _run_command("keybase {} api -m '{}'".format(service, query))
    response = json.loads(response)
    return dict_to_ntuple(response)


def _api_chat(query: dict):
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


def _api_team(query: dict):
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


def _api_wallet(query: dict):
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


def _get_memberships(username: str):
    """Get a dictionary of the teams to which the specified user belongs.

    Parameters
    ----------
    username : str
        The target user.

    Returns
    -------
    team_dict : dict
        A dict comprising named tuples for each of the teams to which the user
        belongs, corresponding with their roles and the number of users in each
        team. The elements are accessed as follows:

        **team_dict[team_name].role** : list
            The role assigned to the user for this team.
        **team_dict[team_name].member_count** : int
            The number of members in this team.
        **team_dict[team_name].data** : namedtuple
            The team info returned from the Keybase Team API.

    """
    # Get the list of team memberships.
    response = _api_team(
        {
            "method": "list-user-memberships",
            "params": {"options": {"username": username}},
        }
    )
    # Extract the important data from the result.
    team_dict = dict()
    if response.result.teams is not None:
        for team in response.result.teams:
            user_role = ["iadmin", "reader", "writer", "admin", "owner"][
                team.role
            ]
            team_data = {
                "role": user_role,
                "member_count": team.member_count,
                "data": team,
            }
            team_dict[team.fq_name] = dict_to_ntuple(team_data)
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
    attempt. After the third failed attempt, it will raise the TimeoutExpired
    error. Any other error encountered will be raised regardless.

    Parameters
    ----------
    command_string : str
        The command to be executed.

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
