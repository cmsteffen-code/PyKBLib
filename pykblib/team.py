"""Defines the Team class."""

from steffentools import dict_to_ntuple

from pykblib.api import KeybaseAPI
from pykblib.exceptions import APIException, KeybaseException, TeamException


class Team:
    """The primary point of interaction with Keybase teams.

    Attributes
    ----------
    name : str
        The name of the team.
    role : str
        The active user's role within the team.
    members_by_role : namedtuple
        A namedtuple comprising unordered sets of members by specified role. To
        access the sets, use one of the following:

        * **Team.members_by_role.owner**
        * **Team.members_by_role.admin**
        * **Team.members_by_role.writer**
        * **Team.members_by_role.reader**
        * **Team.members_by_role.deleted**
        * **Team.members_by_role.reset**

    """

    def __init__(self, team_name, keybase_instance):
        """Initialize the Team class.

        Parameters
        ----------
        team_name : str
            The team's name.
        keybase_instance : Keybase
            The Keybase object that spawned this Team.

        """
        self._api = KeybaseAPI()
        self._keybase = keybase_instance
        self.members_by_role = None  # Populated by self.update()
        self.name = team_name
        self.role = "None"
        self.update()

    def add_member(self, username, role="reader"):
        """Add the specified user to this team.

        *Note: This function is simply a wrapper for the `Team.add_members`
        function, where the username_list parameter contains only one item.*

        Parameters
        ----------
        username : str
            The username of the user to add to the team.
        role : str
            The role to assign to the new member. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team. *(Defaults to reader.)*

        Raises
        ------
        TeamException
            If the user could not be added, a TeamException is raised.

        """
        self.add_members([username], role)

    def add_members(self, username_list, role="reader"):
        """Add the specified users to this team.

        *Note: Keybase adds the specified users one at a time, but still
        returns an error if any of the users cannot be added to the team. For
        example, if the first two users are successfully added to the team, but
        the third user fails, the function will raise an error, despite the
        fact that the first two users were successfully added. As a result, if
        an attempt to add multiple users fails, it is advised to run the
        `Team.update()` function to update the member lists, to determine
        whether any of the specified users were successfully added.*

        Parameters
        ----------
        usernames : str
            The usernames of the users to add to the team.
        role : str
            The role to assign to the new members. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team. *(Defaults to reader.)*

        Raises
        ------
        TeamException
            If the users couldn't be added, a TeamException is raised.

        """
        query = {
            "method": "add-members",
            "params": {
                "options": {
                    "team": self.name,
                    "usernames": [
                        {"username": username, "role": role}
                        for username in username_list
                    ],
                }
            },
        }
        try:
            self._api.call_api("team", query)
            roles = self.members_by_role._asdict()
            roles[role] = roles[role].union(set(username_list))
            self.members_by_role = dict_to_ntuple(roles)
        except APIException:
            raise TeamException(
                "Could not add members to team {}.".format(self.name)
            )

    def change_member_role(self, username, new_role):
        """Change the specified user's role within this team.

        Parameters
        ----------
        username : str
            The username of the member whose role will be changed.
        new_role : str
            The role to assign to the member. This must be either reader,
            writer, admin, or owner. In order to assign the owner role, the
            current user must be an owner of the team.

        Raises
        ------
        TeamException
            If the user's role could not be changed, a TeamException is raised.

        """
        query = {
            "method": "edit-member",
            "params": {
                "options": {
                    "team": self.name,
                    "username": username,
                    "role": new_role,
                }
            },
        }
        try:
            self._api.call_api("team", query)
        except APIException:
            raise TeamException(
                "Could not change member {} to role {} in team {}.".format(
                    username, new_role, self.name
                )
            )
        member_dict = self.members_by_role._asdict()
        for key in member_dict.keys():
            if key == new_role:
                member_dict[key].add(username)
            elif username in member_dict[key]:
                member_dict[key].remove(username)

    def create_sub_team(self, sub_team_name):
        """Create a sub-team within this team.

        This function simply calls `Keybase.create_team` with the appropriate
        full team name, a concatenation of the parent team and sub-team names,
        separated by a period.

        Parameters
        ----------
        sub_team_name : str
            The name of the sub-team to be created. The final team name will be
            `parent.sub_team_name` where `parent` is this team's name.

        Raises
        ------
        TeamException
            If the sub-team cannot be created, a TeamException is raised.

        """
        full_name = "{}.{}".format(self.name, sub_team_name)
        try:
            return self._keybase.create_team(full_name)
        except KeybaseException:
            raise TeamException(
                "Could not create sub-team {}.".format(full_name)
            )

    def delete(self):
        """Delete this team and all of its sub-teams.

        *Note: This is simply a wrapper for the Keybase.delete_team function,
        passing this team's name as the team to be deleted.*

        Raises
        ------
        KeybaseException
            If the team cannot be deleted, a KeybaseException is raised.

        """
        self._keybase.delete_team(self.name)

    def ignore_request(self, username):
        """Ignore the specified user's request to join this team.

        This function is a wrapper for Keybase.ignore_request, passing this
        team's name and the specified username as the target.

        Raises
        ------
        KeybaseException
            If the request cannot be ignored, a KeybaseException will be
            raised.

        """
        self._keybase.ignore_request(self.name, username)

    def leave(self):
        """Leave this team.

        This function is a wrapper for Keybase.leave_team, passing this team's
        name as the target.

        Raises
        ------
        KeybaseException
            If the active user could not leave the team, a KeybaseException is
            raised.

        """
        self._keybase.leave_team(self.name)

    def list_requests(self):
        """Retrieve all requests to join this team.

        This function is a wrapper for Keybase.list_requests, retrieving and
        returning only the set of usernames requesting access to this team.

        Returns
        -------
        usernames : set
            A set containing all the users who have requested access to this
            team.

        Raises
        ------
        KeybaseException
            Should an error occur, this function will raise a KeybaseException.

        """
        return self._keybase.list_requests(self.name)[self.name]

    def members(self):
        """Retrieve a set of the usernames of all members in the team.

        *Note: This includes users who have deleted or reset their accounts.*

        Returns
        -------
        members : set
            A set of the usernames of all members in the team.

        """
        return set(
            set().union(
                *[
                    member_set
                    for member_set in self.members_by_role._asdict().values()
                ]
            )
        )

    def purge_deleted(self):
        """Purge members whose accounts were deleted.

        This function is a wrapper for Team.remove_member, which automatically
        targets members who have deleted their accounts.

        *Note: Even if a TeamException is raised, it's possible that some of
        the deleted users were successfully removed. The usernames listed in
        Team.members_by_role.deleted will contain those that were unable to be
        purged.*

        Raises
        ------
        TeamException
            If some or all of the deleted users could not be purged, a
            TeamException will be raised.

        """
        deleted_users = self.members_by_role.deleted
        success = True
        for user in deleted_users:
            try:
                self.remove_member(user)
            except TeamException:
                success = False
        if not success:
            raise TeamException(
                "Failed to remove all deleted users from team {}.".format(
                    self.name
                )
            )

    def purge_reset(self):
        """Purge members whose accounts were reset.

        This function is a wrapper for Team.remove_member, which automatically
        targets members who have reset their accounts.

        *Note: Even if a TeamException is raised, it's possible that some of
        the reset users were successfully removed. The usernames listed in
        Team.members_by_role.reset will contain those that were unable to be
        purged.*

        Raises
        ------
        TeamException
            If some or all of the reset users could not be purged, a
            TeamException will be raised.

        """
        reset_users = self.members_by_role.reset
        success = True
        for user in reset_users:
            try:
                self.remove_member(user)
            except TeamException:
                success = False
        if not success:
            raise TeamException(
                "Failed to remove all reset users from team {}.".format(
                    self.name
                )
            )

    def remove_member(self, username):
        """Remove the specified user from this team.

        Parameters
        ----------
        username : str
            The username of the user to remove from the team.

        Raises
        ------
        TeamException
            If the user cannot be removed, a TeamException is raised.

        """
        query = {
            "method": "remove-member",
            "params": {"options": {"team": self.name, "username": username}},
        }
        try:
            self._api.call_api("team", query)
            member_dict = self.members_by_role._asdict()
            for member_set in member_dict.values():
                if username in member_set:
                    member_set.remove(username)
        except APIException:
            raise TeamException(
                "Could not remove member {} from team {}.".format(
                    username, self.name
                )
            )

    def rename(self, new_name):
        """Rename this team.

        Note: This will only work if this team is a sub-team.

        Parameters
        ----------
        new_name : str
            The sub-team's new name.

        Raises
        ------
        TeamException
            If the team couldn't be renamed, a TeamException is raised.

        """
        old_full_name = self.name
        old_name = self.name.split(".")[-1]
        new_full_name = old_full_name.replace(old_name, new_name)
        query = {
            "method": "rename-subteam",
            "params": {
                "options": {
                    "team": old_full_name,
                    "new-team-name": new_full_name,
                }
            },
        }
        try:
            self._api.call_api("team", query)
        except APIException:
            raise TeamException(
                "Could not rename sub-team {} to {}.".format(
                    old_full_name, new_full_name
                )
            )
        self._keybase._update_team_name(old_full_name, new_full_name)

    def sub_team(self, sub_team_name):
        """Return a Team instance referring to the specified sub-team.

        Parameters
        ----------
        sub_team_name : str
            The name of the sub-team.

        Returns
        -------
        Team
            If successful, the script will return a Team instance referring
            to the sub-team.

        """
        return self._keybase.team("{}.{}".format(self.name, sub_team_name))

    def update(self):
        """Update the team's membership and role information.

        Changes in membership and role information that were not instigated by
        PyKBLib will not automatically be reflected in the Team. This function
        can be used to update this information.

        Raises
        ------
        TeamException
            If an error is received from the API when trying to retrieve the
            team's membership information, the TeamException will be raised.

        """
        query = {
            "method": "list-team-memberships",
            "params": {"options": {"team": self.name}},
        }
        response = self._api.call_api("team", query)
        members_by_role = dict()
        roles = {
            "owner": response.result.members.owners,
            "admin": response.result.members.admins,
            "writer": response.result.members.writers,
            "reader": response.result.members.readers,
        }
        members_by_role["deleted"] = set()
        members_by_role["reset"] = set()
        for role, member_list in roles.items():
            members_by_role[role] = set()
            if member_list is not None:
                for member in member_list:
                    if member.username == self._keybase.username:
                        # This is our entry, save our role.
                        self.role = role
                    if member.status == 2:
                        # This member has deleted their account.
                        members_by_role["deleted"].add(member.username)
                    elif member.status == 1:
                        # This member's account was reset.
                        members_by_role["reset"].add(member.username)
                    else:
                        # This member is active.
                        members_by_role[role].add(member.username)
        self.members_by_role = dict_to_ntuple(members_by_role)

    def _update_parent_team_name(self, old_name, new_name):
        """Update this team's name after a parent team has changed its name.

        Parameters
        ----------
        old_name : str
            The original name of the parent team.
        new_name : str
            The new name of the parent team.

        """
        self.name = self.name.replace(old_name, new_name)
