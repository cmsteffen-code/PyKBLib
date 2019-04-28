Managing Team Members
=====================

Listing Requests to Join a Team
-------------------------------
When a user requests access to your team, if the team is set as "open," their request will automatically be approved. However, if the team is not open, then you'll need to be able to determine which users have requested access to which teams. To do this, you can use either the `Keybase.list_requests` function or the `Team.list_requests` function.

The `Keybase.list_requests` function allows you to specify an optional team name. If you don't specify the team name, the function will return a `defaultdict` containing sets of the usernames requesting access to each team:

```
>>> KB.list_requests()
defaultdict(<class 'set'>, {'pykblib_dev_team.testing': {'demo_user'}, 'pykblib_dev_team': {'demo_user', 'second_user'}})
```

The dictionary returned is in the format `{team_name: {set of usernames}}`.

If you choose to specify the name of the team, the `Keybase.list_requests` function will return a dictionary containing only the requests for the specified team.

If you've already created an instance of a team and you wish to list the requests for that team, you can also use the `Team.list_requests` function:

```
>>> TEAM.list_requests()
{'demo_user', 'second_user'}
```

The `Team.list_requests` function will return a set containing only the usernames of members who have requested access to that specific team.

Ignoring Requests to Join a Team
--------------------------------
To ignore an incoming request, you can use the `Keybase.ignore_request` function, or if you've already got an instance of the team, you can use the `Team.ignore_request` function. The `Keybase.ignore_request` function requires two arguments, the team name and username:

```
KB.ignore_request("pykblib_dev_team.testing", "demo_user")
```

On the other hand, the `Team.ignore_request` function only requires the username:

```
TEAM.ignore_request("demo_user")
```

This will ignore the specified user's request, and will prevent that user from making additional requests.

Should the function fail to ignore the request, a `KeybaseException` will be raised.

Adding and Removing Members
---------------------------
To add or remove members from a team, you must be an admin or owner of that team. Adding and removing individual team members can be done with the `Team.add_member` and `Team.remove_member` functions, respectively. For example:

```
# Add the 'pykblib' user to the TEAM.
TEAM.add_member("pykblib")
# Remove the 'pykblib' user from the TEAM.
TEAM.remove_member("pykblib")
```

To add multiple members at once, you can use the `Team.add_members` function. It works just like the `Team.add_member` function, except it takes a list of usernames as the first parameter:

```
# Add the 'pykblib' and 'user2' users to the TEAM.
TEAM.add_members(["pykblib", "user2"])
```

The `Team.add_member` and `Team.add_members` functions assign the `reader` role to new members by default. In order to assign a different role, simply specify it as an additional parameter to the `Team.add_member` or `Team.add_members` functions:

```
# Add the 'pykblib' user to the TEAM as a writer.
TEAM.add_member("pykblib", "writer")
# Add the 'user2' and 'user3' users to the TEAM as writers.
TEAM.add_members(["user2", "user3"], "writer")
```

The role assigned must be one of the following:

* `reader` - Can read and write to chat, and can read the team's KBFS resources, including Git repositories.
* `writer` - Can write to the team's KBFS resources, including Git repositories.
* `admin` - Can add or remove admins, readers, and writers to the team, and can establish new sub-teams. They can also deactivate sub-teams.
* `owner` - Can do anything admins can do, but also has the ability to delete the team.

(For more information regarding roles, see [the official Keybase team documentation](https://keybase.io/docs/teams/design). *Note: While each of these roles may have the specified abilities, many of these abilities have not yet been implemented in PyKBLib.*)

If any of the add- or remove-member functions should fail, a `TeamException` will be raised. However, there is a caveat: When using `Team.add_members`, the Keybase API will attempt to add each member in the list in the order they are presented, and will return an error if any of the users are already in the team (resulting in the function raising an exception). However, due to the fact that it adds each member in order, it is possible that some of the members may be successfully added prior to the member that caused the failure.

If an exception is raised, you can use the `Team.update` function to retrieve the latest membership and role information for the team.

Changing Member Roles
---------------------
To change a member's role, the active user must have either the `admin` or `owner` role in the team. Changing a member's role can be accomplished with the `Team.change_member_role` function:

```
# Change the 'pykblib' user's role from writer to reader.
TEAM.change_member_role("pykblib", "reader")
```

Should the function fail, a `TeamException` will be raised.

*Note: Only team owners can add new team owners.*

Purging Deleted and Reset Members
---------------------------------
If a team member deletes or resets their account without leaving a team, their username will be added to the `Team.deleted` or `Team.reset` sets, respectively. (This change will be reflected the next time you run the `Team.update` function.) The `Team.purge_deleted` and `Team.purge_reset` functions were created in order to purge these users quickly. Usage is simple:

```
# Purge all deleted users from a team.
TEAM.purge_deleted()
# Purge all reset users from a team.
TEAM.purge_reset()
```

Should one of the functions fail to purge all the necessary accounts, it will raise a `TeamException` However, it's still possible that some of the users were purged, even though an exception was raised. The exception simply means that the function failed to purge _all_ of the specified users. Fortunately, the `Team.members_by_role` attribute will be updated to reflect the remaining users in the deleted/reseet sets, regardless of whether an exception was raised or not.

*Note: These functions remove all of the users known to be reset or deleted as of the last time `Team.update` was run. If a user reset or deleted their account since the last update was run, another update will be required for those changes to be detected.*
