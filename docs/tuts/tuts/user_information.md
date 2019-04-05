Accessing User Information
==========================

Retrieving the Username
-----------------------
The active user's username is stored in the `Keybase.username` attribute. For example, to print the username, you could do the following:

```
print(KB.username)
```

Retrieving the Team List
------------------------
To retrieve a list of the teams to which the active user belongs, simply use the `Keybase.teams` attribute. For example, to print the list, you could do the following:

```
print("Team Memberships:")
for team_name in KB.teams:
    print(f" - {team_name}")
```

Updating the Team List
----------------------
The `Keybase.teams` list is populated when the `Keybase` class is instantiated. However, it does not actively track changes in the active user's memberships. The `update_team_list` function is used to update this list. To update the list of team memberships, simply do the following:

```
KB.update_team_list()
```

Note that calling this function will incur a slight delay, as the library must request the data from the Keybase application, which can take some time.

Requesting Access to a Team
---------------------------
To join a team, you must first request access to that team. To do this, use the `Keybase.request_access` function, like so:

```
KB.request_access("pykblib_dev_team")
```

If the specified team is an open team, you'll be granted access automatically (though this can take some time). If the specified team is a closed team, you'll only be granted access if the admins or owners decide to do so. To check whether you've been added to the team yet, you can update the team list and see if the team is listed:

```
KB.update_team_list()
if "pykblib_dev_team" in KB.teams:
    print("I'm in!")
```

Leaving a Team
--------------
To leave a team, you can use one of two methods. First, you could use the `Keybase.leave_team` function, which requires you to specify the name of the team you wish to leave:

```
KB.leave_team("pykblib_dev_team")
```

Second, if you've already created an instance of the team (as detailed in the "Managing Teams" section of the documentation), you can simply call the `Team.leave` function:

```
TEAM = KB.team("pykblib_dev_team")
TEAM.leave()
```
