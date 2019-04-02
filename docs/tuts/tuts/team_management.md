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

Sub-teams can have their own sub-teams, which can be created and renamed in the manner outlined here. *However, as of this release, renaming a sub-team doesn't automatically update its sub-sub-teams' names.* If you have a sub-team with sub-teams, and you change the parent sub-team's name, you'll need to manually update that sub-team's sub-teams' names. (Don't worry, we're working on it.)

Deleting Teams
--------------
As of this release, Keybase does not yet support automated team deletion. To delete a team, you will need to be the owner of the team, and you will need to delete it manually, using the `keybase team delete <team_name>` command.
