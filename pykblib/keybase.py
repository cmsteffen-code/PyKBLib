"""The Keybase class."""

from pykblib.functions import _api_team, _get_memberships, _get_username
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
        Team or False
            If the team is successfully created, this function will return a
            Team object for the new team. Otherwise, it will return False.

        """
        query = {
            "method": "create-team",
            "params": {"options": {"team": team_name}},
        }
        # Create the new team.
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        # Add the team to the teams list.
        self.teams.append(team_name)
        self.teams.sort()
        # Create a new Team instance for the new team.
        team_instance = self.team(team_name)
        # Append the new Team to the _active_teams dictionary.
        self._active_teams[team_name] = team_instance
        return team_instance

    def team(self, team_name):
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
            Returns `True` or `False`, dependent on whether the update was
            successful.

        """
        try:
            # Update the teams list.
            for team_name in self.teams:
                if old_name in team_name:
                    self.teams[self.teams.index(team_name)] = team_name.replace(old_name, new_name)
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
