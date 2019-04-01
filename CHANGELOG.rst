Release History
===============

In-Development
--------------
- Expand Team functionality.

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
