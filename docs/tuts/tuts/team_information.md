Interacting with Teams
======================

Retrieving a Team List
----------------------
To retrieve a list of the teams to which the active user belongs, simply use the `teams` attribute of the `Keybase` class. You can use this, for example, to print out the list:

```
print("Team Memberships:")
for team_name in KB.teams:
    print(f" * {team_name}")
```

Updating the Team List
----------------------
The `teams` list is populated when the `Keybase` class is instantiated. However, it does not actively track changes in the active user's memberships. The `update_team_list` function is used to update this list. To update the list of team memberships, simply do the following:

```
KB.update_team_list()
```

Note that calling this function will incur a slight delay, as the library must request the data from the Keybase application, which can take some time.

Creating a Team Instance
------------------------
To interact with a team directly, you'll want to create an instance of the `Team` class. This can be done by using the `team` function from the `Keybase` class:

```
TEAM = KB.team("team_name")
```

The above code will create a `Team` instance connected to the team called "team_name". (You'll want to change "team_name" to the name of the team with which you wish to interact.) It is possible to access team information without assigning the output from the `team` function to a variable, like so:

```
team_name = "team_name"
member_count = KB.team(team_name).member_count
print(f"The '{team_name}' team has {member_count} members.")
```

However, if you need to interact with the team more than once, it is best to store the `Team` instance in a variable, as in the first example. Each time you instantiate a `Team`, there will be a slight delay as the script communicates with the Keybase app, so it's faster to store the `Team` object in a variable rather than creating it repeatedly.

In the following tutorials, we'll refer to the `TEAM` variable when showing how to interact with `Team` objects.

Accessing Team Information
--------------------------
Most information about a team is accessible through the `Team` class' attributes. So far, the following attributes have been implemented:

* `Team.name` (*str*) The name of the team.
* `Team.member_count` (*int*) The number of members in the team.
* `Team.roles` (*list*) A list of the team roles assigned to the current user.

If you wanted to print out a summary of this information, you could do the following:

```
print(f"Information for team {TEAM.name}:")
print(f"- member_count: {TEAM.member_count}")
print(f"- roles: {', '.join(TEAM.roles)}")
```
