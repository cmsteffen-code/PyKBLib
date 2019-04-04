Managing Teams
==============

Creating a New Team
-------------------
To create a new Keybase team, simply use the `Keybase.create_team` function:

```
new_team = KB.create_team("team_name")
```

The `Keybase.create_team` function returns either a new `Team` instance, or `False` if a new team could not be created. Once a new team is created, its name is added to the `Keybase.teams` list.

Keep in mind, team names can only be up to 16 characters long.

To create sub-teams, use the `Team.create_sub_team` function:

```
>>> new_sub_team = new_team.create_sub_team("sub_team_name")
>>> print(new_sub_team.name)
team_name.sub_team_name
```

The name of the resulting sub-team will be `parent_team_name.sub_team_name`.

Renaming Sub-Teams
------------------
If you wish to re-name a sub-team, you can use the `Team.rename` function:

```
>>> new_sub_team.rename("new_name")
>>> print(new_sub_team.name)
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
