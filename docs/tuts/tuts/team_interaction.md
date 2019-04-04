Interacting with Teams
======================

Creating a Team Instance
------------------------
To interact with a team directly, you'll want to create an instance of the `Team` class. This can be done by using the `Keybase.team` function:

```
TEAM = KB.team("team_name")
```

The above code will create a `Team` instance connected to the team called "team_name". (You'll want to change "team_name" to the name of the team with which you wish to interact.) It is possible to access team information without assigning the output from the `Keybase.team` function to a variable, like so:

```
team_name = "team_name"
member_count = len(KB.team(team_name).members())
print(f"The '{team_name}' team has {member_count} members.")
```

However, if you need to interact with the team more than once, it is best to store the `Team` instance in a variable, as in the first example. Each time you instantiate a `Team`, there will be a slight delay as the script communicates with the Keybase app, so it's faster to store the `Team` object in a variable rather than creating it repeatedly.

In the following tutorials, we'll refer to the `TEAM` variable when showing how to interact with `Team` objects.

Accessing Team Information
--------------------------
Most information about a team is accessible through the `Team` class' attributes. So far, the following attributes have been implemented:

* `Team.name` (*str*) The name of the team.
* `Team.role` (*str*) The team role assigned to the current user.
* `Team.members_by_role` (*namedtuple*) A namedtuple containing lists of members sorted into their respective roles:
    * `Team.members_by_role.owner` (*list*) A list of all the owners of the team.
    * `Team.members_by_role.admin` (*list*) A list of all the admins of the team.
    * `Team.members_by_role.writer` (*list*) A list of all the writers in the team.
    * `Team.members_by_role.reader` (*list*) A list of all the readers in the team.
    * `Team.members_by_role.deleted` (*list*) A list of members who have deleted their accounts.
    * `Team.members_by_role.reset` (*list*) A list of members who have reset their accounts.

You can also get a complete list of active members using the `Team.members` function.

If you wanted to print out a summary of this information, you could do the following:

```
print(f"Information for team {TEAM.name}:")
print(f"- role: {TEAM.role}")
print("- team members:")
for member in TEAM.members():
    print(f"  - {member}")
roles = {
    "owners": TEAM.members_by_role.owner,
    "admins": TEAM.members_by_role.admin,
    "writers": TEAM.members_by_role.writer,
    "readers": TEAM.members_by_role.reader,
    "deleted accounts": TEAM.members_by_role.deleted,
    "reset accounts": TEAM.members_by_role.reset,
}
for role, member_list in roles.items():
    print(f"- {role}")
    for member in member_list:
        print(f"  - {member}")
```

The membership and role information is populated at the creation of the `Team` instance. Any time the library is used to update team member information, those changes are saved as well. However, any changes made outside the script will not be automatically recorded. In order to update the team membership information, simply use the `Team.update` function:

```
# Update the team's membership and role information.
TEAM.update()
```

Note that this function incurs a slight delay, due to the fact that it must retrieve fresh information from Keybase.

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

If the `Team.add_member` or `Team.add_members` functions succeed, they will return `True`. Otherwise, they will return `False`. However, there is a caveat: When using `Team.add_members`, the Keybase API will attempt to add each member in the list in the order they are presented, and will return an error if any of the users are already in the team (resulting in the function returning `False`). However, due to the fact that it adds each member in order, it is possible that some of the members may be successfully added prior to the member that caused the failure. For example:

```
>>> # Current members: None
>>> TEAM.add_member("user1")  #1
True
>>> # Current members: user1
>>> TEAM.add_members(["user1", "user2"])  #2
False
>>> # Current members: user1 (user2 wasn't added)
>>> TEAM.add_members(["user2", "user1", "user3"])  #3
False
>>> # Current members: user1, user2 (user3 wasn't added)
```

In the first example (#1), user1 was added to the team successfully. In the second example (#2), user2 could not be added because the API threw an error when trying to add user1, who was already a member of the team. In the third example (#3) user2 was added successfully, but user3 was not added, because the API threw an error when trying to add user1 to the team.

Changing Member Roles
---------------------
To change a member's role, the active user must have either the `admin` or `owner` role in the team. Changing a member's role can be accomplished with the `Team.change_member_role` function:

```
# Change the 'pykblib' user's role from writer to reader.
TEAM.change_member_role("pykblib", "reader")
```

The function will return `True` if the role is successfully changed, or `False` if the role change is a failure. *Note: Only team owners can add new team owners.*

Purging Deleted and Reset Members
---------------------------------
If a team member deletes or resets their account without leaving a team, their username will be added to the `Team.deleted` or `Team.reset` lists, respectively. The `Team.purge_deleted` and `Team.purge_reset` functions were created in order to purge these users quickly. Usage is simple:

```
# Purge all deleted users from a team.
TEAM.purge_deleted()
# Purge all reset users from a team.
TEAM.purge_reset()
```

The functions will return a list of usernames that were unable to be purged, if any. If all deleted/reset users were successfully purged, the functions will return an empty list. Either way, the team's `purged` and `deleted` lists will be updated appropriately.

*Note: The `Team.purge_deleted` function removes all of the users in the current `Team.deleted` list, but it does not automatically update this list.*
