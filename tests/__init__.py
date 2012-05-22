import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import logging

from mock import Mock
from mockito.mockito import when
from b3.config import XmlConfigParser, CfgConfigParser
from b3.parsers.iourt41 import Iourt41Parser
from b3.plugins.admin import AdminPlugin
from urtserversidedemo import UrtserversidedemoPlugin


def write(*args, **kwargs):
    print "WRITE: %s" % args[0]
    return ""

class Iourt41_TestCase_mixin(unittest.TestCase):
    """
    Test case that makes Iourt41Parser inherits from FakeConsole
    """

    @classmethod
    def setUpClass(cls):
        # less logging
        logging.getLogger('output').setLevel(logging.ERROR)

        from b3.parsers.q3a.abstractParser import AbstractParser
        from b3.fake import FakeConsole
        AbstractParser.__bases__ = (FakeConsole,)
        # Now parser inheritance hierarchy is :
        # Iourt41Parser -> AbstractParser -> FakeConsole -> Parser



class Iourt41TestCase(Iourt41_TestCase_mixin):
    """
    Test case that is suitable for testing Iourt41 parser specific features
    """

    def setUp(self):
        # create a Iourt41 parser
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        self.console = Iourt41Parser(self.parser_conf)

        self.console.write = Mock(name="write", side_effect=write)
        self.console.startup()


        # load the admin plugin
        self.adminPlugin = AdminPlugin(self.console, '@b3/conf/plugin_admin.xml')
        self.adminPlugin.onStartup()

        # make sure the admin plugin obtained by other plugins is our admin plugin
        def getPlugin(name):
            if name == 'admin':
                return self.adminPlugin
            else:
                return self.console.getPlugin(name)
        self.console.getPlugin = getPlugin


    def tearDown(self):
        self.console.working = False



class PluginTestCase(Iourt41TestCase):
    """
    Test case ready to test the UrtserversidedemoPlugin
    """
    CONF = ""

    def setUp(self):
        Iourt41TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.conf.loadFromString(self.__class__.CONF)
        self.p = UrtserversidedemoPlugin(self.console, self.conf)
        when(self.console).write('cmdlist startserverdemo').thenReturn("""\
startserverdemo
1 commands
""")
        self.p.onStartup()
        logger = logging.getLogger('output')
        logger.setLevel(logging.NOTSET)

