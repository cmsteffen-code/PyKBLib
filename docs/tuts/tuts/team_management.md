Managing Teams
==============

Creating an Instance of an Existing Team
----------------------------------------
To interact with an existing team, you'll want to create an instance of the `Team` class. This can be done by using the `Keybase.team` function:

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

Creating a New Team
-------------------
To create a new Keybase team, simply use the `Keybase.create_team` function:

```
TEAM = KB.create_team("team_name")
```

The `Keybase.create_team` function returns either a new `Team` instance, or `False` if a new team could not be created. Once a new team is created, its name is added to the `Keybase.teams` list.

Keep in mind, team names can only be up to 16 characters long.

To create sub-teams, use the `Team.create_sub_team` function:

```
>>> SUB_TEAM = TEAM.create_sub_team("sub_team_name")
>>> print(SUB_TEAM.name)
team_name.sub_team_name
```

The name of the resulting sub-team will be `parent_team_name.sub_team_name`.

Renaming Sub-Teams
------------------
If you wish to re-name a sub-team, you can use the `Team.rename` function:

```
>>> SUB_TEAM.rename("new_name")
>>> print(SUB_TEAM.name)
team_name.new_name
```

While parent teams cannot be renamed, sub-teams can be renamed as often as you'd like.

Deleting Teams
--------------
In order to delete a team, you must first be that team's owner.

There are two ways to delete a team in PyKBLib. You can either use the `Keybase.delete_team` function to delete a team by name, or you can delete a team from its instance by using the `Team.delete` function. For example:

```
# Delete team_one by name.
KB.delete_team("team_one")

# Create an instance of team_two and delete it.
TEAM = KB.team("team_two")
TEAM.delete()
```

If you attempt to delete a team that has sub-teams, the sub-teams will be deleted first.

Accessing Team Information
--------------------------
Most information about a team is accessible through the `Team` class' attributes:

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
