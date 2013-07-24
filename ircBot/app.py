"""
Basic IRC bot in python powered by gevent. Most of this is currently borrowed
  from https://gist.github.com/maxcountryman/676306 but is slowly being
  rewritten or heavily modified
"""
import gevent

from ircConnector import IrcConnector
from dispatch import BotDispatch
from sparkfunBot import sparkfunBot

from log import setupLog


#class JoshBot(ChannelBot):
    #personal = True
    #def processMsg(self, who, said):
        #logger.debug("Hi Josh! " + said)
        #self.reply("Hi Josh! " + said)


if __name__ == '__main__':
    logger = setupLog()

    connection = IrcConnector()
    connection.run()

    bots = [
      sparkfunBot("#josh-test"),
      #JoshBot("JoshAshby-SFE")
    ]

    dispatcher = BotDispatch(bots, connection)
    dispatcher.dispatch()
