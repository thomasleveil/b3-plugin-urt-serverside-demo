# -*- encoding: utf-8 -*-
from mock import Mock
from mockito import when
from time import sleep
from b3.fake import FakeClient
from tests import PluginTestCase
from b3.events import eventManager, Events, Event


EVT_BAD_GUID = eventManager.createEvent('EVT_BAD_GUID', 'Bad guid detected')
EVT_1337_PORT = eventManager.createEvent('EVT_1337_PORT', '1337 port detected')


class Test_without_haxbusterurt(PluginTestCase):
    CONF = """\
[commands]
startserverdemo = 20

[haxbusterurt]
demo_duration: 2
"""

    def setUp(self):
        PluginTestCase.setUp(self)
        eventManager = Events()
        self.p.onLoadConfig()
        self.p.onStartup()

    def test_isHaxbusterurtPluginActive(self):
        self.assertFalse(self.p.isHaxbusterurtPluginActive())

    def test_register_events(self):
        self.assertIn(EVT_BAD_GUID, self.p.events)
        self.assertIn(EVT_1337_PORT, self.p.events)


class HaxbusterurtPlugin():
    """
    dummy HaxbusterurtPlugin
    """
    def __init__(self, console):
        self.working = True


class Test_with_haxbusterurt(PluginTestCase):
    CONF = """\
[commands]
startserverdemo = 20

[haxbusterurt]
demo_duration: 2
"""

    def setUp(self):
        PluginTestCase.setUp(self)

        # create a fake haxbusterurt plugin
        self.haxbusterurt = HaxbusterurtPlugin(self.p.console)
        when(self.console).getPlugin('haxbusterurt').thenReturn(self.haxbusterurt)

        self.p.onLoadConfig()
        self.p.onStartup()

    def tearDown(self):
        PluginTestCase.tearDown(self)


    def test_isHaxbusterurtPluginActive(self):
        self.assertTrue(self.p.isHaxbusterurtPluginActive())
        self.haxbusterurt.working = False
        self.assertFalse(self.p.isHaxbusterurtPluginActive())


    def test_register_events(self):
        self.assertIn(EVT_BAD_GUID, self.p.events)
        self.assertIn(EVT_1337_PORT, self.p.events)


    def test_event_EVT_BAD_GUID(self):
        # GIVEN
        self.p._haxbusterurt_demo_duration = (1.0/60)/8 # will make the auto-stop timer end after 125ms
        self.p.start_recording_player = Mock()
        self.p.stop_recording_player = Mock()
        joe = FakeClient(console=self.console, name="Joe", guid="JOE_GUID")
        joe.connects("2")

        # WHEN the haxbusterurt plugin detects that Joe has a contestable guid
        self.console.queueEvent(Event(EVT_BAD_GUID, data=joe.guid, client=joe))

        # THEN
        self.p.start_recording_player.assert_called_with(joe, None)

        # WHEN
        sleep(.2)
        # THEN
        self.p.stop_recording_player.assert_called_with(joe)


    def test_event_EVT_1337_PORT(self):
        # GIVEN
        self.p._haxbusterurt_demo_duration = (1.0/60)/8 # will make the auto-stop timer end after 125ms
        self.p.start_recording_player = Mock()
        self.p.stop_recording_player = Mock()
        joe = FakeClient(console=self.console, name="Joe", guid="JOE_GUID")
        joe.connects("2")

        # WHEN the haxbusterurt plugin detects that Joe has a contestable guid
        self.console.queueEvent(Event(EVT_1337_PORT, data=joe.guid, client=joe))

        # THEN
        self.p.start_recording_player.assert_called_with(joe, None)

        # WHEN
        sleep(.2)
        # THEN
        self.p.stop_recording_player.assert_called_with(joe)

