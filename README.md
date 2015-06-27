b3-plugin-urt-serverside-demo
=============================

A [BigBrotherBot][B3] plugin to take advantage of the Urban Terror server-side demo recording feature.
For every server-side demo started, you will find in the B3 log a _INFO_ line with demo filename, player name, player guid and player ip.

******
*NOTE: since B3 v1.10.1 beta this plugin has been included in the standard plugins set, thus all patches and updates will be performed in the official B3 repository.*
******

Requirements
------------

* B3 v1.8.1 or later
* ioUrTded game server with server-side demo capabilities. See the official [Urban Terror forums][1].


Download
--------

Latest version available at https://github.com/courgette/b3-plugin-urt-serverside-demo/zipball/master


Installation
------------

* copy the urtserversidedemo.py file into b3/extplugins
* copy the plugin_urtserversidedemo.ini file into your config directory
* add to the plugins section of your main b3 config file:
```
    <plugin name="urtserversidedemo" config="@b3/extplugins/conf/plugin_urtserversidedemo.ini" />
```

Usage
-----

#### !startserverdemo \<player\>

Starts a server-side demo.

If _player_ is `all`, then all connected players will be recorded and future connecting players will also be recorded.
Else, starts recording a demo for the given player only.



#### !stopserverdemo \<player\>

Stops recording a server-side demo.

If _player_ is `all`, then all currently recording server-side demos are stopped and future connecting players won't get automatically recorded.
Else, stops all currently recording demos.


#### HaxBusterUrt plugin

This plugin can get notifications from the HaxBusterUrt plugin that a connecting player is suspected of cheating. By
setting a value for `demo_duration` in the `haxbusterurt` section of your config file, demos will automatically be taken for
such players.
Of course you need to have the HaxBusterUrt plugin installed and loaded for this to work, and furthermore, you need to
make sure that the HaxBusterUrt plugin is loaded **before** this plugin.

See the HaxBusterUrt plugin at : http://forum.bigbrotherbot.net/downloads/?sa=view;down=61


#### Follow plugin

This plugin can get notifications from the Follow plugin when a player is found in the follow list. By
setting a value for `demo_duration` in the `follow` section of your config file, demos will automatically be taken for
such players.
Of course you need to have the Follow plugin installed and loaded for this to work, and furthermore, you need to
make sure that the HaxBusterUrt plugin is loaded **before** this plugin.

See the Follow plugin at : http://forum.bigbrotherbot.net/downloads/?sa=view;down=52


Support
-------

If you found a bug or have a suggestion for this plugin, please report it on the B3 forums at http://forum.bigbrotherbot.net/plugins-by-courgette/server-side-demo-(urt)/



Changelog
---------

### 1.0
2012-05-23
* add commands __!startserverdemo__ and __!stopserverdemo__
* able to auto start demo of connecting players if `!startserverdemo all` was called

### 2.0
2012-10-08
* when trying to start a demo on a player which is not fully connected, will wait and retry when the player joins
* can detect the HaxBusterUrt plugin and auto-start demo for player suspected of cheating
* support both demo file extensions : dm_68 and urtdemo

### 2.1
2012-10-09
* can detect the Follow plugin and auto-start demo for player found in the follow list. See http://forum.bigbrotherbot.net/releases/follow-users-plugin/


[B3]: http://www.bigbrotherbot.net/ "BigBrotherBot (B3)"
[1]: http://www.urbanterror.info/forums/topic/28657-server-side-demo-recording/ "Urban Terror forums"


[![Build Status](https://secure.travis-ci.org/courgette/b3-plugin-urt-serverside-demo.png?branch=master)](http://travis-ci.org/courgette/b3-plugin-urt-serverside-demo)

[![Flattr this](http://api.flattr.com/button/flattr-badge-large.png "Flattr this")](https://flattr.com/submit/auto?user_id=tomdesinto&url=https://github.com/courgette/b3-plugin-urt-serverside-demo&title=b3-plugin-urt-serverside-demo&language=en&tags=github,BigBrotherBot&category=software)
