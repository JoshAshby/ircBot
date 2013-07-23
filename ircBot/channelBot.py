import logging
logger = logging.getLogger("irc.bot")

from gevent import queue
import config as c


class ChannelBot(object):
    personal = False

    def __init__(self, channel):
        self.channel = channel
        self._msgQueue = queue.Queue()

    def watch(self):
        while True:
            what = self._msgQueue.get()

            if self.channel[0] != "#" and \
                 what["channel"] == c.nick and \
                 self.personal:
                channel = what["who"]

            else:
                channel = what["channel"]

            if channel.lower() == self.channel.lower():
                logger.debug("In " + self.channel + " " + what["who"] + " said: " + what["said"])
                self.processMsg(who=what["who"], said=what["said"])

    def processMsg(self, who, said):
        pass

    def reply(self, msg, action="PRIVMSG"):
      self._sendMsgQueue.put({"cmd": action, "msg": msg, "channel": self.channel})
