# -*- encoding: utf-8 -*-
from mock import Mock
from mockito import when
from time import sleep
from b3.fake import FakeClient
from tests import PluginTestCase
from b3.events import eventManager, Events, Event


EVT_FOLLOW_CONNECTED = eventManager.createEvent('EVT_FOLLOW_CONNECTED', 'EVT_FOLLOW_CONNECTED')


class FollowPlugin():
    """
    dummy FollowPlugin
    """
    def __init__(self, console):
        self.working = True


class Test_with_follow(PluginTestCase):
    CONF = """\
[commands]
startserverdemo = 20

[follow]
demo_duration: 2
"""

    def setUp(self):
        PluginTestCase.setUp(self)

        # create a fake haxbusterurt plugin
        self.follow = FollowPlugin(self.p.console)
        when(self.console).getPlugin('follow').thenReturn(self.follow)

        self.p.onLoadConfig()
        self.p.onStartup()

    def tearDown(self):
        PluginTestCase.tearDown(self)


    def test_register_events(self):
        self.assertIn(EVT_FOLLOW_CONNECTED, self.p.events)


    def test_event_EVT_FOLLOW_CONNECTED(self):
        # GIVEN
        self.p._follow_demo_duration = (1.0/60)/8 # will make the auto-stop timer end after 125ms
        self.p.start_recording_player = Mock()
        self.p.stop_recording_player = Mock()
        joe = FakeClient(console=self.console, name="Joe", guid="JOE_GUID")
        joe.connects("2")

        # WHEN the haxbusterurt plugin detects that Joe has a contestable guid
        self.console.queueEvent(Event(EVT_FOLLOW_CONNECTED, data=None, client=joe))

        # THEN
        self.p.start_recording_player.assert_called_with(joe, None)

        # WHEN
        sleep(.2)
        # THEN
        self.p.stop_recording_player.assert_called_with(joe)

