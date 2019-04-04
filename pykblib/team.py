"""The Team class."""

from steffentools import dict_to_ntuple

from pykblib.functions import _api_team


# TODO: add Team.update_parent_team_name
class Team:
    """An instance of a Keybase team.

    Attributes
    ----------
    name : str
        The name of the team.
    role : str
        The role assigned to the active user within this team.
    members : list
        A list of the usernames of all active members in the team.
    members_by_role : namedtuple
        A namedtuple comprising lists of members by specified role. To access
        the lists, use one of the following:

        * **Team.members_by_role.owner**
        * **Team.members_by_role.admin**
        * **Team.members_by_role.writer**
        * **Team.members_by_role.reader**
        * **Team.members_by_role.deleted**
        * **Team.members_by_role.reset**

    """

    def __init__(self, name, parent):
        """Initialize the Team class.

        Parameters
        ----------
        name : str
            The team's name.
        parent : Keybase
            The Keybase object that spawned this Team.

        """
        self.name = name
        self._keybase = parent
        # Update the member lists.
        assert self.update()

    def add_member(self, username, role="reader"):
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

    def add_members(self, usernames, role="reader"):
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
        roles = {
            "owner": self.members_by_role.owner,
            "admin": self.members_by_role.admin,
            "writer": self.members_by_role.writer,
            "reader": self.members_by_role.reader,
        }
        roles[role] += usernames
        return True

    def change_member_role(self, username, role):
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
        roles = {
            "owner": self.members_by_role.owner,
            "admin": self.members_by_role.admin,
            "writer": self.members_by_role.writer,
            "reader": self.members_by_role.reader,
        }
        for member_role, member_list in roles.items():
            # Remove the user from their previous role and add them to their
            # new role.
            if role != member_role and username in member_list:
                member_list.pop(member_list.index(username))
            elif role == member_role and username not in member_list:
                member_list.append(username)
        return True

    def create_sub_team(self, team_name):
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
        return self._keybase.create_team(full_name)

    def members(self):
        """Return a list of all active members in the team.

        Returns
        -------
        members : list
            A list of all active members in the team.

        """
        active_member_lists = [
            self.members_by_role.owner,
            self.members_by_role.admin,
            self.members_by_role.writer,
            self.members_by_role.reader,
        ]
        members = list()
        for member_list in active_member_lists:
            members += member_list
        members = sorted(list(set(members)))
        return members

    def purge_deleted(self):
        """Purge deleted members from this team.

        Returns
        -------
        failures : list
            A list of members that were unable to be deleted. If all members
            were deleted successfully, this list will be empty.

        """
        failures = list()
        for username in self.members_by_role.deleted:
            if not self.remove_member(username):
                failures.append(username)
        self.members_by_role.deleted = list(failures)
        return failures

    def purge_reset(self):
        """Purge members whose accounts were reset.

        Returns
        -------
        failures : list
            A list of members that were unable to be purged. If all members
            were purged successfully, this list will be empty.

        """
        failures = list()
        for username in self.members_by_role.reset:
            if not self.remove_member(username):
                failures.append(username)
        self.members_by_role.reset = list(failures)
        return failures

    def remove_member(self, username):
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
        roles = {
            "owner": self.members_by_role.owner,
            "admin": self.members_by_role.admin,
            "writer": self.members_by_role.writer,
            "reader": self.members_by_role.reader,
        }
        for _, member_list in roles.items():
            # Remove the user from their previous role.
            if username in member_list:
                member_list.pop(member_list.index(username))
        return True

    def rename(self, new_name):
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
        self._keybase.update_team_name(self.name, new_name)
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
        self.reset = list()
        roles = {
            "owner": response.result.members.owners,
            "admin": response.result.members.admins,
            "writer": response.result.members.writers,
            "reader": response.result.members.readers,
        }
        members_by_role["deleted"] = list()
        members_by_role["reset"] = list()
        for role, member_list in roles.items():
            try:
                members_by_role[role] = list()
                for member in member_list:
                    if member.username == self._keybase.username:
                        # This is our entry, save our role.
                        self.role = role
                    if member.status == 2:
                        # This member has deleted their account.
                        members_by_role["deleted"].append(member.username)
                    elif member.status == 1:
                        # This member's account was reset.
                        members_by_role["reset"].append(member.username)
                    elif member.status == 0:
                        # This member is active.
                        members_by_role[role].append(member.username)
                    else:
                        # This member is of an unknown status.
                        print(
                            "Unknown member status for {}: {}".format(
                                member.username, member.status
                            )
                        )
                        members_by_role[role].append(member.username)
            except TypeError:
                # We've already initialized the list for this role, so we don't
                # need to worry about handling this exception.
                pass
        self.members_by_role = dict_to_ntuple(members_by_role)
        return True

    def update_parent_team_name(self, old_name, new_name):
        """Update this team's name after a parent team has changed its name.

        Note: This is automatically called when the parent team's name is
        changed. This should not be called directly.

        Parameters
        ----------
        old_name : str
            The original name of the parent team.
        new_name : str
            The new name of the parent team.

        """
        self.name = self.name.replace(old_name, new_name)
