"""Defines the core Keybase class."""

from collections import defaultdict

from pykblib.api import KeybaseAPI
from pykblib.exceptions import APIException, KeybaseException, TeamException
from pykblib.team import Team


class Keybase:
    """Provides a high-level interface for interacting with Keybase.

    Attributes
    ----------
    teams : list
        The list of teams to which the active user belongs.
    username : str
        The username of the active user.

    """

    def __init__(self):
        """Ensure that the class has everything it needs to succeed."""
        self._active_teams = dict()
        self._api = KeybaseAPI()
        self.username = self._get_username()
        self.teams = list()
        self.update_team_list()

    def _get_username(self):
        """Retrieve the username of the active user.

        Returns
        -------
        username : str
            The username of the active user.

        Raises
        ------
        KeybaseException
            If there is not a user logged in, the function will raise a
            KeybaseException.

        """
        status = self._api.run_command("status")
        [userline, statusline] = status.split("\n")[:2]
        username = userline.split()[1]
        online = statusline.split()[2]
        if online == "no":
            raise KeybaseException("User must be logged in.")
        return username

    def create_team(self, team_name):
        """Create a team with the specified name.

        Parameters
        ----------
        team_name : str
            The name of the team to be created.

        Raises
        ------
        KeybaseException
            If the team can't be created, a KeybaseException is raised.

        """
        query = {
            "method": "create-team",
            "params": {"options": {"team": team_name}},
        }
        success = True
        try:
            response = self._api.call_api("team", query)
            if not hasattr(response.result, "creatorAdded"):
                success = False
        except APIException:
            success = False
        if not success:
            raise KeybaseException(
                "Could not create team {}.".format(team_name)
            )
        self.teams.append(team_name)
        return self.team(team_name)

    def delete_team(self, team_name):
        """Delete the specified team, and all of its sub-teams.

        Parameters
        ----------
        team_name : str
            The name of the team to be deleted.

        Raises
        ------
        KeybaseException
            If the team isn't in the Keybase.teams list, or if an APIException
            is raised when attempting to call the KeybaseAPI.delete_team
            function, this function will raise a KeybaseException.

        """
        teams_to_delete = sorted(
            [team for team in self.teams if team.startswith(team_name)],
            key=len,
            reverse=True,
        )
        if team_name not in teams_to_delete:
            raise KeybaseException(
                "Active user is not a member of team {}.".format(team_name)
            )
        for team in teams_to_delete:
            try:
                self._api.delete_team(team)
                self.teams.pop(self.teams.index(team))
                if team in self._active_teams.keys():
                    del self._active_teams[team]
            except APIException:
                raise KeybaseException(
                    "Could not delete team {}.".format(team)
                )

    def ignore_request(self, team_name, username):
        """Ignore a user's access request to the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team.
        username : str
            The name of the user to ignore.

        Raises
        ------
        KeybaseException
            If the request could not be ignored, the function will raise a
            KeybaseException.

        """
        try:
            self._api.run_command(
                "team ignore-request {} -u {}".format(team_name, username)
            )
        except APIException as exception:
            if "Not found" not in exception.message:
                raise KeybaseException(
                    "Failed to ignore request by {} to join {}.".format(
                        username, team_name
                    )
                )

    def leave_team(self, team_name):
        """Leave the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Raises
        ------
        KeybaseException
            If the user could not leave the team, the function will raise a
            KeybaseException.

        """
        query = {
            "method": "leave-team",
            "params": {"options": {"team": team_name, "permanent": False}},
        }
        try:
            self._api.call_api("team", query)
        except APIException as exception:
            if "not a member" not in exception.message:
                raise KeybaseException(
                    "Could not leave team {}.".format(team_name)
                )
        if team_name in self.teams:
            self.teams.pop(self.teams.index(team_name))
        if team_name in self._active_teams.keys():
            del self._active_teams[team_name]

    def list_requests(self, team_name=None):
        """Retrieve a dictionary of all access requests for the specified team.

        If no team is specified, the dictionary will contain all requests for
        all teams.

        Parameters
        ----------
        team_name : str
            The name of the target team. Defaults to None.

        Returns
        -------
        requests : dict
            A dict with team names for keys and sets of usernames as values.

        Raises
        ------
        KeybaseException
            If the function couldn't retrieve the list of access requests, it
            will raise a KeybaseException.

        """
        command = "team list-requests"
        command += " -t {}".format(team_name) if team_name else ""
        result = self._api.run_command(command)
        if "To handle requests" not in result and "No requests" not in result:
            raise KeybaseException("Could not retrieve access requests.")
        lines = [line.strip() for line in result.split("\n")]
        requests = defaultdict(set)
        for line in lines:
            if "wants to join" in line:
                parts = line.split()
                team_name = parts[0]
                user_name = parts[1]
                requests[team_name].add(user_name)
        return requests

    def request_access(self, team_name):
        """Request access to the specified team name.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Raises
        ------
        KeybaseException
            If the request could not be sent, the function will raise a
            KeybaseException.

        """
        try:
            result = self._api.run_command(
                "team request-access {}".format(team_name)
            )
            if (
                "an email has been sent" not in result
                and "You have joined" not in result
            ):
                raise KeybaseException(
                    "Could not request access to {}.".format(team_name)
                )
        except APIException as exception:
            if "already requested" not in exception.message:
                raise KeybaseException(
                    "Could not request access to {}.".format(team_name)
                )

    def team(self, team_name):
        """Return a Team class instance for the specified team.

        Parameters
        ----------
        team_name : str
            The name of the team to which the Team class should refer.

        Returns
        -------
        Team
            If successful, the script will return a `Team` instance referring
            to the specified team.

        Raises
        ------
        KeybaseException
            If the team instance could not be created, a KeybaseException is
            raised.

        """
        try:
            new_team = Team(team_name, self)
            self._active_teams[team_name] = new_team
            return new_team
        except TeamException:
            raise KeybaseException(
                "Could not create team {}.".format(team_name)
            )

    def update_team_list(self):
        """Update the list of teams to which the active member belongs."""
        query = {
            "method": "list-user-memberships",
            "params": {"options": {"username": self.username}},
        }
        response = self._api.call_api("team", query)
        team_set = set()
        if response.result.teams is not None:
            for team in response.result.teams:
                team_set.add(team.fq_name)
        self.teams = sorted(list(team_set))

    def _update_team_name(self, old_name, new_name):
        """Update the name of a team in the teams list.

        This will also attempt to update the names of any sub-teams that have
        been instantiated.

        Parameters
        ----------
        old_name : str
            The original name of the team.
        new_name : str
            The new name of the team.

        """
        # Update the teams list.
        for team_name in self.teams:
            if old_name in team_name:
                self.teams[self.teams.index(team_name)] = team_name.replace(
                    old_name, new_name
                )
        # Update any registered sub-teams with the new name.
        teams_to_replace = list()
        for name, team in self._active_teams.items():
            if old_name in name:
                team._update_parent_team_name(old_name, new_name)
                teams_to_replace.append(name)
        # Replace renamed sub-teams in the teams list.
        for name in teams_to_replace:
            self._active_teams[
                name.replace(old_name, new_name)
            ] = self._active_teams.pop(name)
