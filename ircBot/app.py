"""
Basic IRC bot in python powered by gevent. Most of this is currently borrowed
  from https://gist.github.com/maxcountryman/676306 but is slowly being
  rewritten or heavily modified
"""
import gevent

from ircConnector import IrcConnector
from dispatch import BotDispatch
from channelBot import ChannelBot

from log import setupLog

import config as c


class JoshBot(ChannelBot):
    personal = True
    def processMsg(self, who, said):
        logger.info("Hi Josh. " + said)


if __name__ == '__main__':
    logger = setupLog()

    connection = IrcConnector()

    gevent.spawn(connection.run)

    testBot = ChannelBot("#josh-Test")
    anotherBot = JoshBot("JoshAshby-SFE")

    dispatcher = BotDispatch([testBot, anotherBot], connection)
    dispatcher.dispatch()
