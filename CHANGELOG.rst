Release History
===============

In-Development
--------------
- Expand Team functionality.
- Implement Chat functionality.
- Implement Wallet functionality.

1.1.0 (2019.04.04)
------------------
- Added the ability to delete teams.
- Switched from the subprocess library to the pexpect library for process management.

1.0.2 (2019.04.03)
------------------
- Fixed a bug where renaming a team didn't update the names of its subteams in the program's memory.

1.0.1 (2019.04.03)
------------------
- Refactored code to split the classes up into their own files.

1.0.0 (2019.04.02)
------------------
- Updated the Team.purge_deleted function and added the Team.purge_reset function.
- Removed Team.member_count variable.
- Refactored code to extract global functions into functions.py and rename pykblib.py to classes.py.
- Renamed the public Team.user variable to the private Team._keybase variable.
- Moved the Team.deleted and Team.reset lists into the Team.members_by_role namedtuple.
- Turned Team.members from a variable into a function.
- Updated documentation to match refactored code.

0.2.2 (2019.04.01)
------------------
- Updated Team.purge_deleted to return a list of members were not removed.
- Added Keybase.create_team function. As of now, teams cannot be easily deleted via scripts.
- Added ability to create sub-teams and change sub-team names.

0.2.1 (2019.04.01)
------------------
- Implemented functions for communicating with the various APIs.
- Updated the _get_memberships function to allow for a specified username.
- Added Team.add_members function.
- Updated Team.add_member function to use Team.add_members function.
- Updated documentation to reflect the addition of Team.add_members.
- Updated Team.change_member_role to use the Team API.
- Updated Team.remove_member to use the Team API.
- Updated Team class to take parent Keybase instance as an argument. This will speed up Team creation slightly.
- Updated Team.update function to use the Team API.
- Updated Team documentation to reflect that the Team.members list will not include deleted accounts.
- Refactored Team class to use the Keybase Team API.

0.2.0 (2019.04.01)
------------------
- Added the Team.change_member_role and Team.purge_deleted functions.
- Updated the documentation to account for the new functions, as well as to rearrange tutorials in a more rational layout.

0.1.0 (2019.03.19)
------------------
- Members can now be added and removed from teams.
- Added various member lists to see what members exist, and what roles they have.
- Cleaned up the code a bit.
- Updated the documentation to reflect the new changes.

0.0.3 (2019.03.18)
------------------
- Expanded documentation to include tutorials for all current functionality.
- Changed some public methods to private methods for cleanliness.
- Implemented basic Team class to allow interaction with teams.

0.0.2 (2019.03.17)
------------------
- Created basic Keybase class for interacting with the Keybase daemon.

0.0.1 (2019.03.16)
------------------
- Created the foundation for distribution of PyKBLib.
