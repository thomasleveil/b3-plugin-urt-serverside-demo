b3-plugin-urt-serverside-demo
=============================

A [BigBrotherBot][B3] plugin to take advantage of the Urban Terror server-side demo recording feature.
For every server-side demo started, you will find in the B3 log a _INFO_ line with demo filename, player name, player guid and player ip.


Requirements
------------

* B3 v1.8.1 or later
* ioUrTded game server with server-side demo capabilities. See the official [Urban Terror forums][1].


Download
--------

no stable release for this plugin yet. Adventurers can have a look at the [github repository][2].


Installation
------------

* copy the urtserversidedemo.py file into b3/extplugins
* copy the plugin_urtserversidedemo.ini file into your config directory
* add to the plugins section of your main b3 config file:
    <plugin name="votemapbf3" config="@b3/extplugins/conf/plugin_votemapbf3.ini" />


Usage
-----

#### !startserverdemo <player>

Starts a server-side demo.

If _player_ is `all`, then all connected players will be recorded and future connecting players will also be recorded.
Else, starts recording a demo for the given player only.



#### !stopserverdemo <player>

Stops recording a server-side demo.

If _player_ is `all`, then all currently recording server-side demos are stopped and future connecting players won't get automatically recorded.
Else, stops all currently recording demos.



Support
-------

During the development stage, discussion is held on the [urbanterror.info forums](http://www.urbanterror.info/forums/topic/28665-urt-serverside-demo-recording-bigbrotherbot-plugin/).



Changelog
---------

### 1.0 <small>2012-05-23</small>
* add commands __!startserverdemo__ and __!stopserverdemo__
* able to auto start demo of connecting players if `!startserverdemo` all was called



[B3]: http://www.bigbrotherbot.net/ "BigBrotherBot (B3)"
[1]: http://www.urbanterror.info/forums/topic/28657-server-side-demo-recording/ "Urban Terror forums"
[2]: https://github.com/courgette/b3-plugin-urt-serverside-demo "github repository"