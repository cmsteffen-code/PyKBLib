"""Test the PyKBLib Chat class."""

from unittest import TestCase, mock

from steffentools import dict_to_ntuple

from pykblib.chat import DirectMessage, TeamChat
from pykblib.exceptions import (
    APIException,
    ChatException,
    KeybaseException,
    TeamException,
)


class TeamChatInitializationTest(TestCase):
    def test_teamchat_init(self):
        pass


class TeamChatTest(TestCase):
    pass


class DirectMessageInitializationTest(TestCase):
    def test_directmessage_init(self):
        pass


class DirectMessageTest(TestCase):
    pass
