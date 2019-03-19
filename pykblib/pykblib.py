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

    @staticmethod
    def team(team_name: str):
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
    name : str
        The name of the team.
    role : str
        The role assigned to the active user within this team.
    member_count : int
        The number of members in the team, as of the object creation time.
    members : list
        A list of the usernames of all members in the team.
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

    # Private Attributes
    # ------------------
    # _member_dict : dict
    #     Contains all of the information provided by the update function,
    #     including the roles and real name of each user. This info is
    #     formatted in a namedtuple, so you can access it like so:
    #
    #     self._member_dict[username].real_name : str
    #     self._member_dict[username].role : str
    #
    #     If the real_name is set to "Deleted", the user has deleted their
    #     account.

    def __init__(self, name: str):
        """Initialize the Team class."""
        self.name = name
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
        try:
            # Attempt to add the specified user to the team.
            result = _run_command(
                "keybase team add-member {} -u {} -r {} -s".format(
                    self.name, username, role
                )
            )
            # Check if the result was a success. If so, the word "Success!"
            # will be in the result string. Otherwise it will be false.
            return "Success!" in result
        except subprocess.CalledProcessError:
            # The attempt was a failure.
            return False

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
        try:
            # Attempt to remove the specified user from the team.
            result = _run_command(
                "keybase team remove-member {} -u {} -f".format(
                    self.name, username
                )
            )
            # Check if the result was a success. If so, the word "Success!"
            # will be in the result string. Otherwise it will be false.
            return "Success!" in result
        except subprocess.CalledProcessError:
            # The attempt was a failure.
            return False

    def update(self):
        """Update the team's membership and role information.

        Returns
        -------
        bool
            A boolean value representing the success or failure of the update.

        """
        try:
            # Get the name of this user.
            this_user = _get_username()
            # Initialize the member dictionary and the member lists.
            member_dict = dict()
            members = list()
            deleted = list()
            # Initialize the member_role dict, which will contain lists of the
            # members in each role.
            members_by_role = dict()
            members_by_role["owner"] = list()
            members_by_role["admin"] = list()
            members_by_role["writer"] = list()
            members_by_role["reader"] = list()
            # Retrieve the current list of members.
            result = _run_command(
                "keybase team list-memberships {}".format(self.name)
            )
            # Extract the important information.
            for line in result.split("\n"):
                # Check to ensure this line is valid.
                if self.name not in line:
                    continue
                # Split each line into its constituent parts.
                # The parts are: [team name, role, username, real name]
                line_parts = line.split()
                # Retrieve the user's role.
                role = line_parts[1]
                # Retrieve the user's username.
                username = line_parts[2]
                # Retrieve the user's real name.
                real_name = " ".join(line_parts[3:])
                # Determine whether the user's account was deleted.
                user_deleted = "(inactive due to account delete)" in real_name
                # Add the information to the member_dict, converting the real
                # name, role, and deletion status into a namedtuple.
                member_dict[username] = dict_to_ntuple(
                    {
                        "deleted": user_deleted,
                        "real_name": real_name,
                        "role": role,
                    }
                )
                # Add the username to the members list.
                members.append(username)
                # If the user was deleted, add them to the deleted list.
                if user_deleted:
                    deleted.append(username)
                # Append the user to the members_by_role dict by role.
                members_by_role[role].append(username)
                # If this is the active user, set their role in the team.
                if username == this_user:
                    self.role = role
            # Assign the member lists and member_dict variables to the team.
            self.members = members
            # Set the member_count attribute.
            self.member_count = len(self.members)
            # Convert members_by_role to a namedtuple and save it to the
            # members_by_role attribute.
            self.members_by_role = dict_to_ntuple(members_by_role)
            self.deleted = deleted
            self._member_dict = member_dict
            # If we've reached this point, we've succeeded in updating the
            # member information. Return True.
            return True
        except subprocess.CalledProcessError:
            # There was an error with the request. Do not update any of the
            # team's variables and return False to indicate failure.
            return False


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
