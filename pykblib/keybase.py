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
    # _team_data : dict
    #     A dictionary of the teams to which the user belongs, corresponding
    #     with their roles and the number of users in each team.

    def __init__(self):
        """Initialize the Keybase class."""
        self.username = _get_username()
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
        response = _api_team(query)
        if hasattr(response, "error"):
            return False
        self.teams.append(team_name)
        self.teams.sort()
        return self.team(team_name)

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
        # Return the new team instance.
        return team_instance

    def update_team_list(self):
        """Update the Keybase.teams attribute."""
        # Retrieve information about the team memberships.
        self._team_data = _get_memberships(self.username)
        # Extract the list of team names and store it in the teams attribute.
        self.teams = list(self._team_data.keys())

    def update_team_name(self, old_name, new_name):
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
