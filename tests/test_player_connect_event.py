from mock import Mock
from b3.events import Event, EVT_CLIENT_JOIN
from tests import PluginTestCase
from b3.fake import FakeClient


class Test_player_connect_event(PluginTestCase):
    CONF = """\
[commands]
startserverdemo = 20
stopserverdemo = 20
"""
    def setUp(self):
        PluginTestCase.setUp(self)

        self.joe = FakeClient(self.console, name="Joe", guid="01230123012301230123", groupBits=1)
        self.joe.clearMessageHistory()

        self.p.start_recording_player = Mock(return_value="")
        self.p.start_recording_player.reset_mock()


    def test_auto_start_demo_of_connecting_players(self):
        # GIVEN
        self.p._recording_all_players = True

        # WHEN
        self.joe.connects("2")
        self.console.queueEvent(Event(EVT_CLIENT_JOIN, self.joe, self.joe))

        # THEN
        self.assertTrue(self.p.start_recording_player.called)
        self.p.start_recording_player.assert_called_with(self.joe)




    def test_do_not_auto_start_demo_of_connecting_players(self):
        # GIVEN
        self.p._recording_all_players = False

        # WHEN
        self.joe.connects("2")

        # THEN
        self.assertFalse(self.p.start_recording_player.called)

