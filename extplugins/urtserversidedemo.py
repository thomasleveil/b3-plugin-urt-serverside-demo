# -*- coding: utf-8 -*-
#
# urtserversidedemo Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 courgette@bigbrotherbot.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
import re
from threading import Timer, Thread, Event as TEvent
from b3.plugin import Plugin
from b3.events import EVT_CLIENT_DISCONNECT, EVT_CLIENT_AUTH, EVT_CLIENT_JOIN, EVT_STOP, EVT_EXIT, Event
from b3.functions import minutesStr

__version__ = '2.1'
__author__ = 'Courgette'

class UrtserversidedemoPlugin(Plugin):

    def __init__(self, console, config=None):
        self._re_startserverdemo_success = re.compile(r"""^startserverdemo: recording (?P<name>.+) to (?P<file>.+\.(?:dm_68|urtdemo))$""")
        self._adminPlugin = None
        self._haxbusterurt_demo_duration = 0 # if the haxbusterurt plugin is present, how long should last demo of cheaters
        self._follow_demo_duration = 0 # if the follow plugin is present, how long should last demo of cheaters
        self._recording_all_players = False # if True, then connecting players will be recorded
        Plugin.__init__(self, console, config)


    ################################################################################################################
    #
    # Plugin interface implementation
    #
    ################################################################################################################

    def onLoadConfig(self):
        """\
        This is called after loadConfig(). Any plugin private variables loaded
        from the config need to be reset here.
        """
        self._load_config_haxbusterurt()
        self._load_config_follow()


    def onStartup(self):
        """\
        Initialize plugin settings
        """
        if not self.has_startserverdemo_cmd():
            self.error("This plugin can only work with ioUrTded server with server-side demo recording capabilities. See http://www.urbanterror.info/forums/topic/28657-server-side-demo-recording/")
            self.disable()
            return
        else:
            self.debug("server has startserverdemo command")

        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        self._registerCommands()

        self._demo_manager = DemoManager(self)

        self.registerEvent(EVT_CLIENT_DISCONNECT)
        self.registerEvent(EVT_CLIENT_AUTH)
        self.registerEvent(EVT_CLIENT_JOIN)

        if self.console.getPlugin('haxbusterurt'):
            self.info("HaxBusterUrt plugin found - we will auto record demos for suspected hackers")

            self.EVT_BAD_GUID = self.console.getEventID('EVT_BAD_GUID')
            if self.EVT_BAD_GUID:
                self.registerEvent(self.EVT_BAD_GUID)
            else:
                self.error("Could not register to HaxBusterUrt EVT_BAD_GUID event. Make sure the HaxBusterUrt plugin is loaded before the UrTServerSideDemo plugin in your b3.xml")

            self.EVT_1337_PORT = self.console.getEventID('EVT_1337_PORT')
            if self.EVT_1337_PORT:
                self.registerEvent(self.EVT_1337_PORT)
            else:
                self.error("Could not register to HaxBusterUrt EVT_1337_PORT event. Make sure the HaxBusterUrt plugin is loaded before the UrTServerSideDemo plugin in your b3.xml")

        else:
            self.info("HaxBusterUrt plugin not found")
            self.EVT_BAD_GUID = self.EVT_1337_PORT = None


        # http://forum.bigbrotherbot.net/releases/follow-users-plugin/
        self._follow_plugin = self.console.getPlugin('follow')
        if self._follow_plugin:
            self.info("Follow plugin found - we will auto record demos for followed players")

            self.EVT_FOLLOW_CONNECTED = self.console.getEventID('EVT_FOLLOW_CONNECTED')
            if self.EVT_FOLLOW_CONNECTED:
                self.registerEvent(self.EVT_FOLLOW_CONNECTED)
            else:
                self.error("Could not register to Follow plugin EVT_FOLLOW_CONNECTED event. Make sure the Follow plugin is loaded before the UrTServerSideDemo plugin in your b3.xml")
        else:
            self.info("Follow plugin not found")



    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if event.type == EVT_CLIENT_DISCONNECT:
            self._demo_manager.on_player_disconnect(event.client)
        elif event.type == EVT_CLIENT_JOIN:
            self.onEventClientJoin(event.client)
        elif event.type in (EVT_STOP, EVT_EXIT):
            self.onEventBotStop()
        elif event.type in (self.EVT_BAD_GUID, self.EVT_1337_PORT):
            self.onHaxBusterUrTEvent(event.client)
        elif event.type == self.EVT_FOLLOW_CONNECTED:
            self.onFollowConnectedEvent(event.client)


    def disable(self):
        """actions to take when the plugin is disabled"""
        was_recording_all_players = self._recording_all_players
        self.stop_recording_all_players()
        if was_recording_all_players:
            self._recording_all_players = True # persist the value so demo can restart when plugin is re-enabled
        Plugin.disable(self)


    def enable(self):
        """actions to take when the plugin is enabled"""
        if self._recording_all_players:
            self.start_recording_all_players()
        Plugin.enable(self)


    ################################################################################################################
    #
    # Events handlers
    #
    ################################################################################################################

    def onEventClientJoin(self, client):
        self._demo_manager.on_player_join(client)
        if self._recording_all_players:
            self.info("auto recording joining player %s on slot %s %s" % (client.name, client.cid, client.guid))
            self._demo_manager.take_demo(client)


    def onEventBotStop(self):
        self.stop_recording_all_players()
        self._demo_manager.shutdown()


    def onHaxBusterUrTEvent(self, client):
        if self._recording_all_players:
            self.info("[haxbusterurt] All players are currently being recorded, nothing to do")
        else:
            self.info("[haxbusterurt] auto recording for %s min player %s on slot %s %s %s" % (self._haxbusterurt_demo_duration, client.name, client.cid, client.guid, client.ip))
            self._demo_manager.take_demo(client, duration=self._haxbusterurt_demo_duration * 60)

    def onFollowConnectedEvent(self, client):
        if self._recording_all_players:
            self.info("[Follow] All players are currently being recorded, nothing to do")
        else:
            self.info("[Follow] auto recording for %s min player %s on slot %s %s %s" % (self._follow_demo_duration, client.name, client.cid, client.guid, client.ip))
            self._demo_manager.take_demo(client, duration=self._follow_demo_duration * 60)


    ################################################################################################################
    #
    # Commands implementations
    #
    ################################################################################################################

    def cmd_startserverdemo(self, data, client, cmd=None):
        """\
        <player> - starts recording a demo for the given player. Use 'all' for all players.
        """
        if not data:
            client.message("specify a player name or 'all'")
            return

        if data == 'all':
            self.start_recording_all_players(admin=client)
            return

        targetted_player = self._adminPlugin.findClientPrompt(data, client)
        if not targetted_player:
            # a player matching the name was not found, a list of closest matches will be displayed
            # we can exit here and the user will retry with a more specific player
            return

        self._demo_manager.take_demo(targetted_player, admin=client)


    def cmd_stopserverdemo(self, data, client, cmd=None):
        """\
        <player> - stops recording a demo for the given player. Use 'all' for all players.
        """
        if not data:
            client.message("specify a player name or 'all'")
            return

        if data.split(' ')[0] == 'all':
            self.stop_recording_all_players(admin=client)
            return

        targetted_player = self._adminPlugin.findClientPrompt(data, client)
        if not targetted_player:
            # a player matching the name was not found, a list of closest matches will be displayed
            # we can exit here and the user will retry with a more specific player
            return

        self._demo_manager.stop_demo(targetted_player, admin=client)




    ################################################################################################################
    #
    # Other methods
    #
    ################################################################################################################

    def _registerCommands(self):
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp
                func = getattr(self, "cmd_" + cmd, None)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
                else:
                    self.warning("config defines unknown command '%s'" % cmd)


    def has_startserverdemo_cmd(self):
        rv = self.console.write('cmdlist startserverdemo')
        return 'startserverdemo' in rv


    def _load_config_haxbusterurt(self):
        try:
            self._haxbusterurt_demo_duration = self.config.getint('haxbusterurt', 'demo_duration')
        except Exception, err:
            self.warning(err)
        self.info('haxbusterurt demo_duration: %s minutes' % self._haxbusterurt_demo_duration)


    def _load_config_follow(self):
        try:
            self._follow_demo_duration = self.config.getint('follow', 'demo_duration')
        except Exception, err:
            self.warning(err)
        self.info('follow demo_duration: %s minutes' % self._follow_demo_duration)


    def start_recording_all_players(self, admin=None):
        self._recording_all_players = True
        rv = self.console.write("startserverdemo all")
        if admin:
            if rv:
                admin.message(rv)
            else:
                admin.message("start recording all players")


    def stop_recording_all_players(self, admin=None):
        self._recording_all_players = False
        rv = self.console.write("stopserverdemo all")
        if admin:
            if rv:
                admin.message(rv)
            else:
                admin.message("stop recording all players")


    def start_recording_player(self, client, admin=None):
        msg_prefix = "" if not admin else "[%s] " % admin.name
        rv = self.console.write("startserverdemo %s" % client.cid)
        match = self._re_startserverdemo_success.match(rv)
        if match:
            self.info("%sstart recording player \"%s\" %s %s : %s" % (msg_prefix, client.name, client.guid, client.ip, match.group('file')))
        else:
            self.warning("%sstart recording player \"%s\" %s %s : %s" % (msg_prefix, client.name, client.guid, client.ip, rv))
        return rv


    def stop_recording_player(self, client, admin=None):
        msg_prefix = "" if not admin else "[%s] " % admin.name
        rv = self.console.write("stopserverdemo %s" % client.cid)
        self.info("%sstop recording player \"%s\" %s %s : %s" % (msg_prefix, client.name, client.guid, client.ip, rv))
        if admin:
            admin.message(rv)



class DemoManager(object):
    """
    class that remembers which demo is being taken, or waiting to be taken
    """
    
    def __init__(self, plugin):
        self.plugin = plugin
        self._demo_starters = {} # dict<guid, DemoStarter>
        self._auto_stop_timers = {} # dict<guid, Timer object for the auto-stopping demos>

    #--------------------------------------------------------------------------------------------
    # public API
    #--------------------------------------------------------------------------------------------

    def take_demo(self, player, admin=None, duration=None):
        """
        Starts a demo for player (and given duration).
        If the player is not in a playing team, wait for player to join or leave the server.
        """
        if player.guid in self._demo_starters:
            # we already have a DemoStarter for that player
            starter = self._demo_starters[player.guid]
            if starter.is_alive():
                starter.cancel()

        if player.guid in self._auto_stop_timers:
            stopper = self._auto_stop_timers[player.guid]
            stopper.cancel()
            del self._auto_stop_timers[player.guid]

        self._demo_starters[player.guid] = DemoStarter(self, player, admin, duration)
        self._demo_starters[player.guid].start()


    def stop_demo(self, player, admin=None):
        if player.guid in self._demo_starters:
            # we already have a DemoStarter for that player
            starter = self._demo_starters[player.guid]
            if starter.is_alive():
                starter.cancel()
        self.plugin.stop_recording_player(player, admin)


    def shutdown(self):
        """
        cancel all DemoStarter objects and stopper timers that would be waiting
        """
        for guid, starter in self._demo_starters.items():
            starter.cancel()
        for guid, stopper in self._auto_stop_timers:
            stopper.cancel()


    def on_player_disconnect(self, player):
        """
        called when a player leaves the game server
        """
        stopper = self._auto_stop_timers.get(player.guid, None)
        if stopper:
            stopper.cancel()
            del self._auto_stop_timers[player.guid]

        starter = self._demo_starters.get(player.guid, None)
        if starter:
            starter.cancel()


    def on_player_join(self, player):
        """
        called when a player joins a team
        """
        stopper = self._auto_stop_timers.get(player.guid, None)
        if stopper:
            stopper.cancel()
            del self._auto_stop_timers[player.guid]

        starter = self._demo_starters.get(player.guid, None)
        if starter:
            starter.tick()


    #--------------------------------------------------------------------------------------------
    # API for DemoStarters only
    #--------------------------------------------------------------------------------------------

    def _done_callback(self, player_guid):
        """
        callback used by DemoStarter objects to notify the manager they are done with their task
        """
        if player_guid in self._demo_starters:
            del self._demo_starters[player_guid]


    def _start_autostop_timer(self, client, duration, admin=None):
        str_duration = minutesStr(duration/60.0)
        self.plugin.info("starting auto-stop demo timer for %s and %s" % (client.name, str_duration))
        t = self._auto_stop_timers.get(client.guid, None)
        if t:
            # stop eventually existing auto-stop timer for that player
            t.cancel()
        t = self._auto_stop_timers[client.guid] = Timer(duration, self._autostop_recording_player, [client])
        t.start()
        if admin:
           admin.message("demo for %s will stop in %s" % (client.name, str_duration))


    #--------------------------------------------------------------------------------------------
    # other methods
    #--------------------------------------------------------------------------------------------

    def _autostop_recording_player(self, client):
        self.plugin.debug("auto-stopping demo for %s" % client.name)
        self.plugin.stop_recording_player(client)
        del self._auto_stop_timers[client.guid]




class DemoStarter(Thread):
    """
    class that will start a server side demo for a given player right away if the player is in a recordable team,
    or as soon as the player join a recordable team (hence will wait until).
    Waiting will be cancelled if the player leaves the server.
    If a duration is provided, will make sure to end the demo after the given duration elapsed.
    """
    STATE_PLAYER_NOT_ACTIVE = 1
    STATE_DEMO_STARTED = 2
    STATE_DEMO_ALREADY_STARTED = 3
    STATE_DEMO_CANNOT_BE_STARTED = 4

    def __init__(self, demo_manager, client, admin=None, duration=None):
        """
        Starts an agent that will start a server-side demo for the given client.
        :param demo_manager: DemoManager object asking for the demo
        :param client: Client object for the player to take the demo of
        :param admin: optional Client object for the admin who ordered the demo
        :param duration: optional duration in second the demo must last (ignored if a demo was already recording that player)
        :return: None
        """
        self.demo_manager = demo_manager
        self.plugin = demo_manager.plugin
        self.client = client
        self.admin = admin
        self.duration = duration
        self._cancel_event = TEvent() # will be used to give up trying
        self._try_event = TEvent() # will be used to trigger another try
        Thread.__init__(self, name="DemoStarter(%s)" % client.name)


    #--------------------------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------------------------

    def run(self):
        while True:
            if self._is_cancelled():
                break
            if not self.plugin.working:
                break
            if not self.client.connected:
                self.plugin.debug("%s: client disconnected" % self.name)
                break

            state, rv = self._try_to_start_demo()
            if state == self.STATE_DEMO_STARTED:
                if self.admin:
                    self.admin.message(rv)
                if self.duration:
                    self.demo_manager._start_autostop_timer(self.client, self.duration, self.admin)
                break
            elif state == self.STATE_PLAYER_NOT_ACTIVE:
                if self.admin:
                    self.admin.message("player %s has not joined the game yet, will retry in a while" % self.client.name)
                self._try_event.wait() # for player to join a team / disconnect or bot to stop
            elif state in (self.STATE_DEMO_ALREADY_STARTED, self.STATE_DEMO_CANNOT_BE_STARTED):
                if self.admin:
                    self.admin.message(rv)
                break
            else:
                raise AssertionError("unexpected state : %s" % state)

        self.demo_manager._done_callback(self.client.guid)
        self.plugin.debug("%s: end" % self.name)


    def tick(self):
        """
        try again to start the demo
        """
        self._try_event.set()
        self._try_event.clear()


    def cancel(self):
        """
        if waiting to try, cancel and stop
        """
        self._cancel_event.set()
        self.tick()


    #--------------------------------------------------------------------------------------------
    # private methods
    #--------------------------------------------------------------------------------------------

    def _try_to_start_demo(self):
        rv = self.plugin.start_recording_player(self.client, self.admin)
        if rv.startswith("startserverdemo: recording "):
            return self.STATE_DEMO_STARTED, rv
        elif rv.endswith("is already being recorded"):
            return self.STATE_DEMO_ALREADY_STARTED, rv
        elif rv.endswith(" is not active"):
            return self.STATE_PLAYER_NOT_ACTIVE, rv
        elif rv.startswith("No player"):
            return self.STATE_DEMO_CANNOT_BE_STARTED, rv
        else:
            raise AssertionError("unexpected response: %r" % rv)


    def _is_cancelled(self):
        return self._cancel_event.is_set()