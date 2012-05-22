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
#
__version__ = '1.0'
__author__ = 'Courgette'

import re
from b3.plugin import Plugin
from b3.events import EVT_CLIENT_DISCONNECT, EVT_CLIENT_AUTH, EVT_CLIENT_JOIN, EVT_STOP, EVT_EXIT


class UrtserversidedemoPlugin(Plugin):

    def __init__(self, console, config=None):
        self._re_startserverdemo_success = re.compile(r"""^startserverdemo: recording (?P<name>.+) to (?P<file>.+\.dm_68)$""")
        self._adminPlugin = None
        self._recording_all_players = False # if True, then connecting players will be recorded

        # when a player connects, it is not yet in-game and demo cannot be taken before he joins the game.
        # this set is to store players we are waiting the join event before starting the demo recording.
        self._players_to_record_after_join = set()

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
        pass


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
        self.registerEvent(EVT_CLIENT_DISCONNECT)
        self.registerEvent(EVT_CLIENT_AUTH)
        self.registerEvent(EVT_CLIENT_JOIN)


    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if event.type == EVT_CLIENT_DISCONNECT:
            self.onEventClientDisconnect(event.client)
        elif event.type == EVT_CLIENT_AUTH:
            self.onEventClientAuth(event.client)
        elif event.type == EVT_CLIENT_JOIN:
            self.onEventClientJoin(event.client)
        elif event.type in (EVT_STOP, EVT_EXIT):
            self.onEventBotStop()


    def disable(self):
        """actions to take when the plugin is disabled"""
        if self._recording_all_players:
            self.stop_recording_all_players()
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

    def onEventClientDisconnect(self, client):
        self._players_to_record_after_join.discard(client)

    def onEventClientAuth(self, client):
        if self._recording_all_players:
            self.debug("auto recording connecting player %s: %s" % (client.cid, client.name))
            self._players_to_record_after_join.add(client)

    def onEventClientJoin(self, client):
        if self._recording_all_players:
            self.info("auto recording joining player %s: %s" % (client.cid, client.name))
            self._players_to_record_after_join.discard(client)
            self.start_recording_player(client)

    def onEventBotStop(self):
        if self._recording_all_players:
            self.stop_recording_all_players()

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
            self.start_recording_all_players()
            return

        targetted_player = self._adminPlugin.findClientPrompt(data, client)
        if not targetted_player:
            # a player matching the name was not found, a list of closest matches will be displayed
            # we can exit here and the user will retry with a more specific player
            return

        client.message(self.start_recording_player(targetted_player))


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

        client.message(self.stop_recording_player(targetted_player))




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
        self._players_to_record_after_join.clear()
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
        return rv