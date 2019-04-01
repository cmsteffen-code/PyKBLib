Accessing User Information
==========================

Retrieving the Username
-----------------------
The active user's username is stored in the `username` attribute of the `Keybase` class. For example, to print the username, you could do the following:

```
username = KB.username
print(f"Currently logged in as {username}.")
```

Retrieving the Team List
------------------------
To retrieve a list of the teams to which the active user belongs, simply use the `Keybase.teams` attribute. You can use this, for example, to print out the list:

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
