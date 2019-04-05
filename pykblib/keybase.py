"""Contains the Keybase class definition."""

import string

from pykblib.functions import (
    _api_team,
    _delete_team,
    _get_memberships,
    _get_username,
    _run_command,
)
from pykblib.team import Team


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
    # _active_teams : dict
    #     A dictionary of all the teams that have been spawned in this session.

    def __init__(self):
        """Initialize the Keybase class."""
        self.username = _get_username()
        self._active_teams = dict()
        self.update_team_list()

    def create_team(self, team_name):
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
        `Team` or `False`
            If successful, the script will return a `Team` instance referring
            to the new team. Otherwise, the function will return `False`.

        """
        query = {
            "method": "create-team",
            "params": {"options": {"team": team_name}},
        }
        # Create the new team.
        response = _api_team(query)
        if hasattr(response, "error"):
            if (
                "already exists" not in response.error.message
                and "already in use" not in response.error.message
            ):
                print("Error creating team: {}".format(response.error.message))
            return False
        # Add the team to the teams list.
        self.teams.append(team_name)
        self.teams.sort()
        # Create a new Team instance for the new team.
        team_instance = self.team(team_name)
        # Append the new Team to the _active_teams dictionary.
        self._active_teams[team_name] = team_instance
        return team_instance

    def delete_team(self, team_name):
        """Attempt to delete the specified team and all of its sub-teams.

        Parameters
        ----------
        team_name : str
            The name of the team to be deleted.

        Returns
        -------
        bool
            `True` or `False`, dependent on whether the function succeeded.

        """
        allowed_characters = string.ascii_letters + string.digits + "_-."
        if any([letter not in allowed_characters for letter in team_name]):
            # We want to prevent any kind of mischief with malformed names.
            return False
        # Compile a list of teams to be deleted.
        teams = [team for team in self.teams if team.startswith(team_name)]
        if team_name not in teams:
            return False
        # Delete each of the returned teams, starting with sub-teams.
        for team in sorted(teams, key=len, reverse=True):
            if not _delete_team(team):
                return False
            # Remove this team's record from self.teams and self._active_teams.
            self.teams.pop(self.teams.index(team))
            if team in self._active_teams.keys():
                team_instance = self._active_teams.pop(team)
                del team_instance
        return True

    @staticmethod
    def ignore_request(team_name, username):
        """Attempt to ignore a user's access request to the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team.
        username : str
            The name of the user to ignore.

        Returns
        -------
        bool
            `True` or `False`, dependent on whether the function succeeded.

        """
        result = _run_command(
            ["keybase", "team", "ignore-request", team_name, "-u", username]
        )
        if "Success!" in result or "not found" in result.lower():
            return True
        return False

    @staticmethod
    def leave_team(team_name):
        """Attempt to leave the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        bool
            `True` or `False`, dependent on whether the function succeeded.

        """
        query = {
            "method": "leave-team",
            "params": {"options": {"team": team_name, "permanent": False}},
        }
        response = _api_team(query)
        if hasattr(response, "error"):
            if "not a member" not in response.error.message:
                return False
        return True

    @staticmethod
    def list_requests(team_name=None):
        """List all requests to join any of the active user's teams.

        If a team is specified, the function will list requests to that
        specific team.

        Parameters
        ----------
        team_name : str
            (optional) The name of the team to be checked.

        Returns
        -------
        usernames : list or tuple
            A list of all the users which have requested access. If there was
            no team name specified, this returns a tuple containing the team
            name and username for each request: `[(team_name, username), ...]`

        """
        command_list = ["keybase", "team", "list-requests"]
        if team_name is not None:
            command_list += ["-t", team_name]
        result = _run_command(command_list)
        requests = [
            line.strip()
            for line in result.split("\n")
            if "wants to join" in line
        ]
        if team_name is None:
            return [(line.split()[0], line.split()[1]) for line in requests]
        return [
            line.split()[1]
            for line in requests
            if line.split()[0] == team_name
        ]

    @staticmethod
    def request_access(team_name):
        """Request access to the specified team name.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        bool
            `True` or `False`, dependent on whether the function succeeded.

        """
        result = _run_command(["keybase", "team", "request-access", team_name])
        if "an email has been sent" in result or "already requested" in result:
            return True
        return False

    def team(self, team_name):
        """Return a Team class instance for the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team to which the Team class should refer.

        Returns
        -------
        `Team` or `False`
            If successful, the script will return a `Team` instance referring
            to the specified team. Otherwise, the function will return `False`.

        """
        # Create the new Team instance.
        team_instance = Team(team_name, self)
        # Append the new Team to the _active_teams dictionary.
        self._active_teams[team_name] = team_instance
        # Return the new team instance.
        return team_instance

    def update_team_list(self):
        """Update the Keybase.teams attribute."""
        self.teams = _get_memberships(self.username)

    def update_team_name(self, old_name, new_name):
        """Attempt to update the name of a team in the teams list.

        This will also attempt to update the names of any sub-teams that have
        been instantiated.

        Parameters
        ----------
        old_name : str
            The original name of the team.
        new_name : str
            The new name of the team.

        Returns
        -------
        bool
            `True` or `False`, dependent on whether the function succeeded.

        """
        try:
            # Update the teams list.
            for team_name in self.teams:
                if old_name in team_name:
                    self.teams[
                        self.teams.index(team_name)
                    ] = team_name.replace(old_name, new_name)
            # Update the team name in the _active_teams dict.
            if old_name in self._active_teams.keys():
                self._active_teams[new_name] = self._active_teams.pop(old_name)
            # Update any registered sub-teams with the new name.
            teams_to_replace = list()
            for name, team in self._active_teams.items():
                if old_name in name:
                    team.update_parent_team_name(old_name, new_name)
                    teams_to_replace.append(name)
            # Replace renamed sub-teams in the teams list.
            for name in teams_to_replace:
                self._active_teams[
                    name.replace(old_name, new_name)
                ] = self._active_teams.pop(name)
            return new_name in self.teams
        except ValueError:
            # The team name wasn't in the list.
            return False
