import logging
logger = logging.getLogger("irc.bot")

from gevent import queue
import config as c


class ChannelBot(object):
    personal  = False

    commands  = False
    cmdPrefix =  "!"

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
                self.who = what["who"]
                self.said = what["said"]

                logger.debug("In " + self.channel + " " + self.who + " said: " + self.said)

                if self.commands:
                    self.searchCmds()

                self.processMsg()

    def searchCmds(self):
        if self.said[0] == self.cmdPrefix:
            try:
                cmd, action = self.said[1:].split(" ", 1)
            except:
                cmd = self.said[1:]
                action = None

            self.runCmd(cmd, action)

    def runCmd(self, cmd, action):
        pass

    def processMsg(self):
        pass

    def sendCmd(self, cmd, msg):
        self._sendMsgQueue({"msg": msg,
                            "channel": self.channel,
                            "action": cmd})

    def reply(self, msg):
      self._sendMsgQueue.put({"msg": msg,
                              "channel": self.channel})

    def replyTo(self, who, msg):
        self._sendMsgQueue.put({"msg": who+": "+msg,
                                "channel": self.channel})
