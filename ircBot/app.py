"""
Basic IRC bot in python powered by gevent. Most of this is currently borrowed
  from https://gist.github.com/maxcountryman/676306 but is slowly being
  rewritten or heavily modified
"""
import gevent

from gevent import queue
from ircConnector import IrcConnector

from log import setupLog


class ChannelBot(object):
    personal = False
    def __init__(self, channel, msgQueue):
        self.channel = channel
        self._msgQueue = msgQueue

    def watch(self):
        while True:
            what = self._msgQueue.get()

            if self.channel[0] != "#" and \
                 what["channel"] == self._conn.nick and \
                 self.personal:
                channel = what["who"]

            else:
                channel = what["channel"]

            if channel.lower() == self.channel.lower():
                self.processMsg(who=what["who"], said=what["said"])

    def processMsg(self, who, said):
        logger.debug("In " + self.channel + " " + who + " said: " + said)


class JoshBot(channelBot):
    personal = True
    def processMsg(self, who, said):
        logger.info("Hi Josh. " + said)


if __name__ == '__main__':
    logger = setupLog()
    logger.debug("HI")

    connection = IrcConnector(nick='JoshAshby',
                       server='irc.freenode.net',
                       port=6667,
                       channels="#josh-test")

    gevent.spawn(connection.run)

    testBot = channelBot("#josh-Test", connection)
    anotherBot = josh_bot("JoshAshby-SFE", connection)

    jobs = [gevent.spawn(testBot.watch),
            gevent.spawn(anotherBot.watch)]
    try:
        gevent.joinall(jobs)
    except KeyboardInterrupt:
        gevent.killall(jobs)
