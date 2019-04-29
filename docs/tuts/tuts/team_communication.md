Communication With Teams
========================

Detecting Available Chat Channels
---------------------------------
To determine which chat channels are available in a team, simply use the `Team.channels` function. This function provides additional useful information as well, such as the active user's status within each channel, and which channels contain unread messages.

The `Team.channels` function returns a dict with channel names as the keys and namedtuples as the values. To get only a list of channel names, you can retrieve the keys from the returned dict:

```
>>> list(TEAM.channels().keys())
['general', 'example_channel_1', 'example_channel_2']
```

To access the user status or determine whether there are unread messages, you can access the `status` and `unread` attributes stored in the dict's values:

```
>>> channels = TEAM.channels()
>>> channels["general"].status
'active'
>>> channels["general"].unread
True
```

If you wanted to display all of the available information, you could use the following code:

```
channels = TEAM.channels()
print(f"Available channels in {TEAM.name}:")
for name, data in channels.items():
    print(f"  - #{name}")
    print(f"      - status: {data.status}")
    unread_messages = "no"
    if data.unread:
        unread_messages = "yes"
    print(f"      - unread messages: {unread_messages}")
```

Which would output something like this:

```
Available channels in hook_and_bobber:
  - #general
      - status: active
      - unread messages: yes
  - #example_channel_1
      - status: active
      - unread messages: no
  - #example_channel_2
      - status: left
      - unread messages: yes
```
